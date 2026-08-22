package com.dykng.medievalarms.client;

import com.dykng.medievalarms.weapon.MedievalWeaponItem;
import com.dykng.medievalarms.weapon.SwingMotion;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.client.extensions.common.IClientItemExtensions;

/**
 * 이 모드 무기의 클라이언트 쪽 동작을 한곳에 모았다.
 *
 * <ul>
 *   <li>{@link #applyForgeHandTransform} — 1인칭에서 손에 든 무기를 어떻게 움직일지</li>
 *   <li>{@link #getArmPose} — 3인칭에서 가만히 들고 있을 때의 자세</li>
 * </ul>
 *
 * <p><b>왜 RenderHandEvent를 쓰지 않는가:</b> 처음에는 그 이벤트를 취소하고 아이템을
 * 직접 그렸다. 하지만 그 이벤트는 바닐라가 {@code pushPose()}를 부르기 전에 발생해
 * 주손과 보조손이 공유하는 바깥쪽 PoseStack을 넘겨주고, 렌더까지 직접 떠맡아야 한다.
 * NeoForge가 바로 이 용도로 마련해둔 {@code applyForgeHandTransform}은 바닐라의
 * push/pop 안쪽에서 호출되므로 변환이 새어나갈 수 없고, 실제 렌더는 바닐라가 그대로 한다.
 * 훨씬 안전하고 다른 모드와도 덜 부딪힌다.
 */
public final class MedievalWeaponClientExtensions implements IClientItemExtensions {

    /** 모든 무기가 같은 규칙을 쓰므로 인스턴스 하나를 돌려쓴다. */
    public static final MedievalWeaponClientExtensions INSTANCE = new MedievalWeaponClientExtensions();

    private MedievalWeaponClientExtensions() {
    }

    // ── 3인칭: 들고 있는 자세 ──────────────────────────────────────────
    @Override
    public HumanoidModel.ArmPose getArmPose(LivingEntity entity, InteractionHand hand, ItemStack stack) {
        if (stack.getItem() instanceof MedievalWeaponItem weapon) {
            return ModArmPoses.forMotion(weapon.getWeaponType().motion);
        }
        return null;
    }

    // ── 1인칭: 휘두르는 동작 ──────────────────────────────────────────

    /**
     * 손에 든 무기의 위치와 각도를 직접 정한다.
     *
     * @return {@code true}면 바닐라의 기본 변환을 건너뛰고 바로 렌더로 넘어간다.
     *         이 모드 무기가 아니면 {@code false}를 돌려 바닐라에 맡긴다.
     */
    @Override
    public boolean applyForgeHandTransform(PoseStack poseStack, LocalPlayer player, HumanoidArm arm,
                                           ItemStack stack, float partialTick,
                                           float equipProcess, float swingProcess) {
        if (!(stack.getItem() instanceof MedievalWeaponItem weapon)) {
            return false;
        }

        applyHandPosition(poseStack, arm, equipProcess);
        applySwing(poseStack, arm, swingProcess, weapon.getWeaponType().motion);
        return true;
    }

    /**
     * 손을 화면 어디에 둘지. 바닐라와 똑같은 값을 쓴다.
     * {@code equipProcess}는 무기를 막 꺼내는 중일 때 아래에서 올라오는 연출이다.
     */
    private static void applyHandPosition(PoseStack poseStack, HumanoidArm arm, float equipProcess) {
        int side = arm == HumanoidArm.RIGHT ? 1 : -1;
        poseStack.translate(side * 0.56F, -0.52F + equipProcess * -0.6F, -0.72F);
    }

    /**
     * 무기 종류에 따라 다른 휘두르기 동작.
     *
     * <p>바닐라의 동작을 뼈대로 삼고 각 축의 크기만 {@link SwingMotion}의 값으로 바꿨다.
     * 모션을 조정하고 싶으면 이 파일이 아니라 {@code SwingMotion}의 숫자만 고치면 된다.
     *
     * <p>진행도가 0일 때(휘두르지 않을 때) 모든 항이 0이 되어 바닐라의 평상시 자세와
     * 정확히 같아진다. 그래서 가만히 들고 있을 때는 다른 아이템과 이질감이 없다.
     */
    private static void applySwing(PoseStack poseStack, HumanoidArm arm, float progress, SwingMotion motion) {
        int side = arm == HumanoidArm.RIGHT ? 1 : -1;

        // 진행도를 모션의 성격에 맞게 다시 매핑한다.
        // speedScale이 1보다 크면 앞부분이 빨라 가볍게, 작으면 느려 묵직하게 느껴진다.
        // 지수를 쓰는 이유는 0과 1을 그대로 유지해 동작이 중간에 잘리지 않게 하기 위함이다.
        float p = (float) Math.pow(Mth.clamp(progress, 0.0F, 1.0F), 1.0F / motion.speedScale);

        // 두 가지 곡선. 둘 다 0에서 시작해 0으로 끝난다.
        float peakMid = Mth.sin(p * p * (float) Math.PI);         // 중반에 가장 크다
        float peakEarly = Mth.sin(Mth.sqrt(p) * (float) Math.PI); // 초반에 가장 크다

        // 1) 시야 기준 이동. 아직 회전 전이라 -Z가 정면, -Y가 아래다.
        //    찌르기는 앞으로, 내리치기는 아래로 움직인다.
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
