package com.dykng.medievalarms.client;

import com.dykng.medievalarms.MedievalArms;
import com.dykng.medievalarms.registry.ModItems;
import com.dykng.medievalarms.weapon.MedievalWeaponItem;

import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.Item;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.EntityRenderersEvent;
import net.neoforged.neoforge.client.extensions.common.RegisterClientExtensionsEvent;

import java.util.ArrayList;
import java.util.List;

/**
 * 클라이언트에서만 필요한 설정을 붙인다.
 *
 * <p>이 모드의 무기 전부에 {@link MedievalWeaponClientExtensions}를 연결한다.
 * 1인칭 휘두르기와 3인칭 자세가 거기 들어 있다.
 *
 * <p>갑옷에는 {@link MedievalArmorClientExtensions}를 연결해 상자가 아닌
 * 모델로 그리게 한다. 그 모델의 뼈대는 여기서 미리 등록해둬야 쓸 수 있다.
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
        List<Item> weapons = new ArrayList<>();
        for (var holder : ModItems.all()) {
            Item item = holder.get();
            if (item instanceof MedievalWeaponItem) {
                weapons.add(item);
            }
        }
        event.registerItem(MedievalWeaponClientExtensions.INSTANCE, weapons.toArray(new Item[0]));

        List<Item> armour = new ArrayList<>();
        for (var holder : ModItems.all()) {
            Item item = holder.get();
            if (item instanceof ArmorItem) {
                armour.add(item);
            }
        }
        event.registerItem(MedievalArmorClientExtensions.INSTANCE, armour.toArray(new Item[0]));
    }

    /**
     * 갑옷 모델의 뼈대를 등록한다.
     *
     * <p>모델은 쓰기 전에 이렇게 등록해둬야 한다. 등록하지 않고 bakeLayer 를 부르면
     * 게임이 그 자리에서 죽는다.
     */
    @SubscribeEvent
    public static void registerLayers(EntityRenderersEvent.RegisterLayerDefinitions event) {
        event.registerLayerDefinition(MedievalArmorModel.HELMET, MedievalArmorModel::createHelmetLayer);
        event.registerLayerDefinition(MedievalArmorModel.CHESTPLATE, MedievalArmorModel::createChestplateLayer);
    }
}
