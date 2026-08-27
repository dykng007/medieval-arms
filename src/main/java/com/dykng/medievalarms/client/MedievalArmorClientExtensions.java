package com.dykng.medievalarms.client;

import net.minecraft.client.Minecraft;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.client.extensions.common.IClientItemExtensions;

/**
 * 갑옷을 그릴 때 바닐라 사람 모델 대신 이 모드의 모델을 쓰게 한다.
 *
 * <p>텍스처만으로는 갑옷이 상자 모양을 벗어날 수 없다. 투구는 머리 큐브 하나,
 * 흉갑은 몸통 큐브 하나라서 실루엣이 정해져 있기 때문이다.
 * {@link MedievalArmorModel} 이 거기에 돔과 바이저, 견갑 큐브를 더한다.
 *
 * <p>부위마다 필요한 큐브가 다르므로 투구와 흉갑에 서로 다른 모델을 돌려준다.
 * 각반과 장화는 추가 큐브가 필요 없어 바닐라 모델을 그대로 쓴다.
 */
public final class MedievalArmorClientExtensions implements IClientItemExtensions {

    public static final MedievalArmorClientExtensions INSTANCE = new MedievalArmorClientExtensions();

    private MedievalArmorClientExtensions() {
    }

    @Override
    public HumanoidModel<?> getHumanoidArmorModel(LivingEntity entity, ItemStack stack,
                                                  EquipmentSlot slot, HumanoidModel<?> original) {
        var models = Minecraft.getInstance().getEntityModels();
        return switch (slot) {
            case HEAD -> new MedievalArmorModel(models.bakeLayer(MedievalArmorModel.HELMET));
            case CHEST -> new MedievalArmorModel(models.bakeLayer(MedievalArmorModel.CHESTPLATE));
            // 각반과 장화는 추가 큐브가 없으니 바닐라 모델 그대로.
            default -> original;
        };
    }
}
