package com.dykng.medievalarms.mixin;

import com.dykng.medievalarms.weapon.MedievalWeaponItem;
import com.dykng.medievalarms.weapon.SwingMotion;

import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * 3인칭에서 <b>휘두르는 동작</b>을 무기 종류마다 다르게 만든다.
 *
 * <p><b>왜 믹스인이어야 하는가:</b> 바닐라 {@code HumanoidModel.setupAnim}은
 * 팔 자세(ArmPose)를 먼저 적용한 뒤 {@code setupAttackAnimation}으로 팔 회전을 덮어쓴다.
 * 그래서 {@link com.dykng.medievalarms.client.ModArmPoses}로는 들고 있는 자세만 바꿀 수 있고
 * 휘두르는 동작은 손댈 수 없다. 그 사이에 끼어들 NeoForge 이벤트도 없다.
 * {@code RenderLivingEvent.Pre}는 모델 계산 전에, {@code Post}는 렌더 후에 발생해 둘 다 늦거나 이르다.
 *
 * <p><b>충돌을 줄이기 위한 선택:</b>
 * <ul>
 *   <li>{@code @At("TAIL")}로 <i>맨 끝에</i> 끼어들어 바닐라 계산을 취소하지 않고 그 위에 값을 더한다.
 *       바닐라의 몸통 비틀림 같은 자연스러운 부분이 그대로 남는다.</li>
 *   <li>이 모드의 무기를 휘두르는 순간에만 개입하고, 그 외에는 즉시 빠져나온다.
 *       다른 전투 모드가 같은 지점을 건드려도 서로 영향이 거의 없다.</li>
 * </ul>
 *
 * <p>이 믹스인은 클라이언트 전용이다. {@code HumanoidModel}은 서버에 존재하지 않으므로
 * {@code medievalarms.mixins.json}의 {@code client} 목록에만 넣어야 한다.
 */
@Mixin(HumanoidModel.class)
public abstract class HumanoidModelMixin {

    /**
     * 바닐라가 스스로 적용하는 내리치기 각도(라디안 1.2 = 약 69도)에 해당하는 값.
     * {@link SwingMotion#strikePitch}가 이 값이면 바닐라와 같은 동작이 되고,
     * 크면 더 내리치고 작으면 더 수평에 가까워진다.
     */
    private static final float VANILLA_PITCH_DEGREES = 69.0F;

    /**
     * 1인칭 기준으로 잡은 각도를 3인칭에 그대로 쓰면 팔이 과장되게 꺾인다.
     * 절반만 반영해 자연스러운 폭으로 맞춘다.
     */
    private static final float THIRD_PERSON_SCALE = 0.5F;

    /** 1인칭과 같은 정규화 상수. {@code MedievalWeaponClientExtensions} 참고. */
    private static final float PHASE_PEAK = 0.58F;

    /** 도 단위를 라디안으로. ModelPart의 회전은 전부 라디안이다. */
    private static final float DEG_TO_RAD = (float) (Math.PI / 180.0);

    @Inject(method = "setupAttackAnimation", at = @At("TAIL"))
    private void medievalarms$applyWeaponSwing(LivingEntity entity, float ageInTicks, CallbackInfo ci) {
        HumanoidModel<?> model = (HumanoidModel<?>) (Object) this;

        float attackTime = model.attackTime;
        if (attackTime <= 0.0F) {
            return;
        }

        // 어느 팔이 휘두르는지. 바닐라 getAttackArm과 같은 규칙을 쓴다
        // (private이라 직접 부를 수 없어 같은 식을 다시 적었다).
        HumanoidArm mainArm = entity.getMainArm();
        HumanoidArm arm = entity.swingingArm == InteractionHand.MAIN_HAND ? mainArm : mainArm.getOpposite();

        // 그 팔에 들려 있는 물건이 이 모드의 무기일 때만 개입한다.
        InteractionHand hand = arm == mainArm ? InteractionHand.MAIN_HAND : InteractionHand.OFF_HAND;
        ItemStack stack = entity.getItemInHand(hand);
        if (!(stack.getItem() instanceof MedievalWeaponItem weapon)) {
            return;
        }

        SwingMotion motion = weapon.getWeaponType().motion;
        ModelPart part = arm == HumanoidArm.RIGHT ? model.rightArm : model.leftArm;
        int side = arm == HumanoidArm.RIGHT ? 1 : -1;

        // 1인칭과 같은 2단 곡선을 쓴다. 그래야 시점을 바꿔도 같은 동작으로 보인다.
        float p = (float) Math.pow(Mth.clamp(attackTime, 0.0F, 1.0F), 1.0F / motion.speedScale);
        float bell = Mth.sin(p * (float) Math.PI);
        float windup = bell * (1.0F - p) / PHASE_PEAK;
        float strike = bell * p / PHASE_PEAK;

        // 바닐라가 이미 적용한 몫을 뺀 '차이'만 더한다. 차이가 0이면 바닐라 그대로다.
        // 바닐라의 기여는 스윙 내내 아래로 내리치는 한 방향이라 strike 쪽에서 상쇄한다.
        float pitchDeg = motion.windupPitch * windup
                - (motion.strikePitch - VANILLA_PITCH_DEGREES) * strike;

        // xRot을 빼면 팔이 아래로 내려간다(바닐라도 같은 부호를 쓴다).
        part.xRot -= pitchDeg * DEG_TO_RAD * THIRD_PERSON_SCALE;
        part.yRot += side * motion.strikeYaw * (windup - strike) * DEG_TO_RAD * THIRD_PERSON_SCALE;

        // 찌르기는 팔을 앞으로 내민다.
        // ModelPart의 좌표는 픽셀 단위(한 블록 = 16)라, 블록 단위 값에 16을 곱한다.
        float reach = motion.windupPull * windup - motion.strikeReach * strike;
        part.z += reach * 16.0F * THIRD_PERSON_SCALE;
    }
}
