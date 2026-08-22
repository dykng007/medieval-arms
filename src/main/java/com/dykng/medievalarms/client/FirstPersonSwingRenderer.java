package com.dykng.medievalarms.client;

import com.dykng.medievalarms.MedievalArms;
import com.dykng.medievalarms.weapon.MedievalWeaponItem;
import com.dykng.medievalarms.weapon.SwingMotion;

import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.RenderHandEvent;
import com.mojang.math.Axis;

/**
 * 1인칭 화면에서 무기를 휘두르는 동작을 무기 종류마다 다르게 그린다.
 *
 * <p>플레이어가 실제로 보는 화면이라 이 모드에서 체감이 가장 큰 부분이다.
 * 믹스인 없이 NeoForge의 {@link RenderHandEvent}만으로 구현했다.
 *
 * <p><b>왜 이벤트에서 PoseStack만 살짝 건드리지 않고 직접 그리는가:</b>
 * 이 이벤트는 바닐라가 {@code pushPose()}를 부르기 <i>전에</i> 발생한다.
 * 즉 여기서 넘어오는 PoseStack은 주손과 보조손 렌더가 공유하는 바깥쪽 스택이다.
 * 그래서 균형을 맞추지 않고 변환을 얹으면 보조손에 든 물건까지 같이 틀어진다.
 * 안전한 방법은 스스로 push - 변환 - 렌더 - pop 을 하고 이벤트를 취소해
 * 바닐라 렌더가 아예 돌지 않게 하는 것뿐이다.
 */
@EventBusSubscriber(modid = MedievalArms.MOD_ID, value = Dist.CLIENT)
public final class FirstPersonSwingRenderer {

    private FirstPersonSwingRenderer() {
    }

    @SubscribeEvent
    public static void onRenderHand(RenderHandEvent event) {
        ItemStack stack = event.getItemStack();
        // 이 모드의 무기가 아니면 바닐라가 알아서 그리게 둔다.
        if (!(stack.getItem() instanceof MedievalWeaponItem weapon)) {
            return;
        }

        Minecraft minecraft = Minecraft.getInstance();
        LocalPlayer player = minecraft.player;
        if (player == null) {
            return;
        }

        // 주손인지 보조손인지에 따라 팔이 왼쪽인지 오른쪽인지가 갈린다.
        // 왼손잡이 설정을 켠 플레이어도 있으므로 getMainArm()을 봐야 한다.
        boolean isMainHand = event.getHand() == net.minecraft.world.InteractionHand.MAIN_HAND;
        HumanoidArm arm = isMainHand ? player.getMainArm() : player.getMainArm().getOpposite();

        // 휘두르는 동작은 주손에서만 일어난다.
        // 보조손에 무기를 들고 있어도 흔들리지 않으므로 진행도를 0으로 둔다.
        float swingProgress = isMainHand ? event.getSwingProgress() : 0.0F;

        PoseStack poseStack = event.getPoseStack();
        poseStack.pushPose();

        applyHandPosition(poseStack, arm, event.getEquipProgress());
        applySwing(poseStack, arm, swingProgress, weapon.getWeaponType().motion);

        minecraft.getEntityRenderDispatcher().getItemInHandRenderer().renderItem(
                player,
                stack,
                arm == HumanoidArm.RIGHT
                        ? ItemDisplayContext.FIRST_PERSON_RIGHT_HAND
                        : ItemDisplayContext.FIRST_PERSON_LEFT_HAND,
                arm == HumanoidArm.LEFT,
                poseStack,
                event.getMultiBufferSource(),
                event.getPackedLight());

        poseStack.popPose();

        // 우리가 다 그렸으니 바닐라 렌더는 건너뛰게 한다.
        event.setCanceled(true);
    }

    /**
     * 손을 화면 어디에 둘지. 바닐라와 똑같은 값을 쓴다.
     * {@code equipProgress}는 무기를 막 꺼내는 중일 때 아래에서 올라오는 연출이다.
     */
    private static void applyHandPosition(PoseStack poseStack, HumanoidArm arm, float equipProgress) {
        int side = arm == HumanoidArm.RIGHT ? 1 : -1;
        poseStack.translate(side * 0.56F, -0.52F + equipProgress * -0.6F, -0.72F);
    }

    /**
     * 무기 종류에 따라 다른 휘두르기 동작.
     *
     * <p>바닐라의 동작을 뼈대로 삼고, 각 축의 크기를 {@link SwingMotion}의 값으로 바꿨다.
     * 그래서 모션을 조정하고 싶으면 이 파일이 아니라 {@code SwingMotion}의 숫자만 고치면 된다.
     *
     * <p>진행도가 0일 때(휘두르지 않을 때) 모든 항이 0이 되어 바닐라의 평상시 자세와 정확히 같아진다.
     */
    private static void applySwing(PoseStack poseStack, HumanoidArm arm, float progress, SwingMotion motion) {
        int side = arm == HumanoidArm.RIGHT ? 1 : -1;

        // 진행도를 모션의 성격에 맞게 다시 매핑한다.
        // speedScale이 1보다 크면 앞부분이 빨라 가볍게 느껴지고,
        // 1보다 작으면 앞부분이 느려 묵직하게 느껴진다.
        // 지수를 쓰는 이유는 0과 1을 그대로 유지해서 동작이 중간에 잘리지 않게 하기 위함이다.
        float p = (float) Math.pow(Mth.clamp(progress, 0.0F, 1.0F), 1.0F / motion.speedScale);

        // 두 가지 곡선. 둘 다 0에서 시작해 0으로 끝난다.
        float peakMid = Mth.sin(p * p * (float) Math.PI);        // 중반에 가장 크다
        float peakEarly = Mth.sin(Mth.sqrt(p) * (float) Math.PI); // 초반에 가장 크다

        // 1) 시야 기준 이동. 아직 회전 전이라 -Z가 정면, -Y가 아래다.
        //    찌르기는 앞으로, 내리치기는 아래로 크게 움직인다.
        poseStack.translate(0.0F,
                -motion.dropDistance * peakEarly,
                -motion.thrustDistance * peakEarly);

        // 2) 회전. 앞뒤의 45도는 바닐라가 손을 화면 안쪽으로 돌려두는 기본 각도라 그대로 둔다.
        poseStack.mulPose(Axis.YP.rotationDegrees(side * (45.0F + peakMid * -20.0F)));
        poseStack.mulPose(Axis.ZP.rotationDegrees(side * peakEarly * -20.0F));
        // 좌우로 후리기 (SWEEP에서 크다)
        poseStack.mulPose(Axis.YP.rotationDegrees(side * peakEarly * -motion.yawDegrees));
        // 위에서 아래로 내리치기 (OVERHEAD/CHOP에서 크다)
        poseStack.mulPose(Axis.XP.rotationDegrees(peakEarly * -motion.pitchDegrees));
        poseStack.mulPose(Axis.YP.rotationDegrees(side * -45.0F));
    }
}
