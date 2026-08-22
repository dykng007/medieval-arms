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
     * 두 단계 곡선의 최대값. 아래 {@code sin(pi*p)*(1-p)} 는 p가 0.35 부근에서
     * 약 0.58로 최대가 된다. 이 값으로 나눠 정규화해두면 {@link SwingMotion}에 적은
     * 숫자가 곧 그 단계에서의 실제 최대 각도/거리가 되어 조정하기 쉽다.
     */
    private static final float PHASE_PEAK = 0.58F;

    /**
     * 무기 종류에 따라 다른 휘두르기 동작.
     *
     * <p>동작을 준비(windup)와 타격(strike) 두 단계로 나눠 적용한다.
     * 두 단계 모두 진행도 0과 1에서 값이 0이 되므로, 휘두르지 않을 때의 자세는
     * 바닐라와 정확히 같고 동작이 끝나는 순간에도 끊기지 않는다.
     *
     * <p>모션을 조정하고 싶으면 이 파일이 아니라 {@link SwingMotion}의 숫자만 고치면 된다.
     */
    private static void applySwing(PoseStack poseStack, HumanoidArm arm, float progress, SwingMotion motion) {
        int side = arm == HumanoidArm.RIGHT ? 1 : -1;

        // 바닐라가 손을 화면 안쪽으로 돌려두는 기본 각도.
        // 이 45도 쌍 사이에 모션을 넣어야 평상시 자세가 다른 아이템과 같아진다.
        poseStack.mulPose(Axis.YP.rotationDegrees(side * 45.0F));

        float p = Mth.clamp(progress, 0.0F, 1.0F);
        if (p > 0.0F) {
            // 완급에 따라 진행도를 다시 매핑한다.
            p = (float) Math.pow(p, 1.0F / motion.speedScale);

            // 시작과 끝에서 0이 되는 종 모양 곡선.
            float bell = Mth.sin(p * (float) Math.PI);
            // 앞쪽에 무게가 실린 단계와 뒤쪽에 실린 단계로 나눈다.
            float windup = bell * (1.0F - p) / PHASE_PEAK;  // 0.35 부근에서 최대
            float strike = bell * p / PHASE_PEAK;           // 0.65 부근에서 최대

            // 앞뒤 이동: 준비 때 몸쪽으로 당겼다가 타격 때 앞으로 내지른다.
            // +Z가 몸쪽, -Z가 앞쪽이다.
            poseStack.translate(0.0F, 0.0F,
                    motion.windupPull * windup - motion.strikeReach * strike);

            // 위아래 회전: 준비 때 치켜들었다가 타격 때 내리친다.
            // 양수가 위, 음수가 아래다.
            poseStack.mulPose(Axis.XP.rotationDegrees(
                    motion.windupPitch * windup - motion.strikePitch * strike));

            // 좌우 회전: 준비 때 바깥으로 열었다가 타격 때 안쪽으로 후린다.
            poseStack.mulPose(Axis.YP.rotationDegrees(
                    side * motion.strikeYaw * (windup - strike)));

            // 손목이 살짝 돌아가는 느낌. 모든 모션에 공통으로 조금씩 준다.
            poseStack.mulPose(Axis.ZP.rotationDegrees(side * -18.0F * strike));
        }

        poseStack.mulPose(Axis.YP.rotationDegrees(side * -45.0F));
    }
}
