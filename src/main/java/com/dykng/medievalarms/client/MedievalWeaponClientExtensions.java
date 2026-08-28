package com.dykng.medievalarms.client;

import com.dykng.medievalarms.weapon.MedievalWeaponItem;

import net.minecraft.client.model.HumanoidModel;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.client.extensions.common.IClientItemExtensions;

/**
 * 이 모드 무기를 <b>가만히 들고 있을 때</b>의 3인칭 자세를 정한다.
 *
 * <p>휘두르는 동작은 여기 없다. 그쪽은
 * {@link com.dykng.medievalarms.client.WeaponAnimations} 가 애니메이션으로 처리한다.
 *
 * <p>예전에는 이 클래스가 {@code applyForgeHandTransform} 으로 1인칭에서 손에 든
 * 아이템을 직접 회전·이동시켰다. 팔도 몸도 움직이지 않아 무기만 허공에서 떠다니는
 * 것처럼 보였고, 숫자를 아무리 맞춰도 그 한계는 넘지 못해 걷어냈다.
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

}
