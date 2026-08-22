package com.dykng.medievalarms.client;

import com.dykng.medievalarms.weapon.SwingMotion;

import net.minecraft.client.model.HumanoidModel;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.entity.LivingEntity;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.api.distmarker.OnlyIn;
import net.neoforged.fml.common.asm.enumextension.EnumProxy;
import net.neoforged.neoforge.client.IArmPoseTransformer;

/**
 * 3인칭에서 무기를 <b>들고 있는 자세</b>를 무기 종류마다 다르게 만든다.
 *
 * <p>마인크래프트는 손에 든 물건에 따라 팔 자세를 {@code ArmPose}라는 목록에서 고른다.
 * 그 목록은 바닐라가 정해둔 것이지만, NeoForge의 확장 열거형 기능으로 항목을 더 넣을 수 있다.
 * 실제로 추가하는 선언은 자바가 아니라
 * {@code src/main/resources/META-INF/enumextensions.json} 에 들어 있고,
 * 그 파일이 아래 {@code EnumProxy} 필드를 가리킨다.
 *
 * <p>주의: 이 자세는 <i>가만히 들고 있을 때</i>만 적용된다. 실제로 휘두르는 순간에는
 * 바닐라가 팔 회전을 덮어써서 여기 값이 무시된다. 3인칭 휘두르기까지 바꾸려면
 * {@code HumanoidModel}에 믹스인을 걸어야 하는데, 그건 별개의 작업이다.
 */
@OnlyIn(Dist.CLIENT)
public final class ModArmPoses {

    private ModArmPoses() {
    }

    /**
     * 창·미늘창 — 자루를 세워 어깨에 기대듯 든다.
     * 두 손으로 드는 자세가 아니므로 첫 인자는 false다.
     */
    public static final EnumProxy<HumanoidModel.ArmPose> POLEARM = new EnumProxy<>(
            HumanoidModel.ArmPose.class,
            false,
            (IArmPoseTransformer) ModArmPoses::applyPolearm);

    /** 철퇴·워해머·전투도끼 — 무거워서 어깨에 걸쳐 든다. */
    public static final EnumProxy<HumanoidModel.ArmPose> SHOULDERED = new EnumProxy<>(
            HumanoidModel.ArmPose.class,
            false,
            (IArmPoseTransformer) ModArmPoses::applyShouldered);

    /**
     * 무기의 동작 종류에 맞는 자세를 고른다.
     * 새 모션을 추가했는데 자세를 정하지 않으면 바닐라 기본값(null)이 되어
     * 평범하게 든 모습이 된다.
     */
    public static HumanoidModel.ArmPose forMotion(SwingMotion motion) {
        return switch (motion) {
            case THRUST, SWEEP -> POLEARM.getValue();
            case OVERHEAD, CHOP -> SHOULDERED.getValue();
            // 베기는 바닐라 검과 같은 평범한 자세가 어울린다.
            case SLASH -> HumanoidModel.ArmPose.ITEM;
        };
    }

    /** 자루를 세워 든 자세. 팔을 앞으로 살짝 들고 위로 세운다. */
    private static void applyPolearm(HumanoidModel<?> model, LivingEntity entity, HumanoidArm arm) {
        // xRot은 라디안이다. 음수가 팔을 앞/위로 든다.
        // -1.4 라디안은 약 -80도로, 자루를 거의 수직으로 세운 모습이 된다.
        if (arm == HumanoidArm.RIGHT) {
            model.rightArm.xRot = -1.4F;
            model.rightArm.yRot = -0.2F;
        } else {
            model.leftArm.xRot = -1.4F;
            model.leftArm.yRot = 0.2F;
        }
    }

    /** 어깨에 걸쳐 든 자세. 팔을 더 크게 접어 올린다. */
    private static void applyShouldered(HumanoidModel<?> model, LivingEntity entity, HumanoidArm arm) {
        if (arm == HumanoidArm.RIGHT) {
            model.rightArm.xRot = -2.1F;
            model.rightArm.yRot = -0.45F;
            model.rightArm.zRot = 0.15F;
        } else {
            model.leftArm.xRot = -2.1F;
            model.leftArm.yRot = 0.45F;
            model.leftArm.zRot = -0.15F;
        }
    }
}
