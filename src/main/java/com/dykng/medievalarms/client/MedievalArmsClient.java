package com.dykng.medievalarms.client;

import com.dykng.medievalarms.MedievalArms;
import com.dykng.medievalarms.registry.ModItems;
import com.dykng.medievalarms.weapon.MedievalWeaponItem;

import net.minecraft.client.model.HumanoidModel;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.extensions.common.IClientItemExtensions;
import net.neoforged.neoforge.client.extensions.common.RegisterClientExtensionsEvent;

import java.util.ArrayList;
import java.util.List;

/**
 * 클라이언트에서만 필요한 설정을 붙인다.
 *
 * <p>여기서는 "이 아이템을 들었을 때 어떤 팔 자세를 쓸 것인가"를 등록한다.
 * 자세 자체는 {@link ModArmPoses}가 정의하고, 이 클래스는 아이템과 자세를 연결만 한다.
 *
 * <p>{@code Dist.CLIENT}로 제한되어 있어 서버에서는 이 클래스가 아예 로드되지 않는다.
 * 그래야 서버에 없는 렌더링 클래스를 건드리다 터지는 일이 없다.
 */
@EventBusSubscriber(modid = MedievalArms.MOD_ID, bus = EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
public final class MedievalArmsClient {

    private MedievalArmsClient() {
    }

    @SubscribeEvent
    public static void registerClientExtensions(RegisterClientExtensionsEvent event) {
        // 이 모드의 무기 전부를 한 번에 등록한다.
        List<Item> weapons = new ArrayList<>();
        for (var holder : ModItems.all()) {
            Item item = holder.get();
            if (item instanceof MedievalWeaponItem) {
                weapons.add(item);
            }
        }

        event.registerItem(new IClientItemExtensions() {
            @Override
            public HumanoidModel.ArmPose getArmPose(LivingEntity entity, InteractionHand hand, ItemStack stack) {
                if (stack.getItem() instanceof MedievalWeaponItem weapon) {
                    return ModArmPoses.forMotion(weapon.getWeaponType().motion);
                }
                return null;
            }
        }, weapons.toArray(new Item[0]));
    }
}
