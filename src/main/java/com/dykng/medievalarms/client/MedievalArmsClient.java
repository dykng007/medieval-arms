package com.dykng.medievalarms.client;

import com.dykng.medievalarms.MedievalArms;
import com.dykng.medievalarms.registry.ModItems;
import com.dykng.medievalarms.weapon.MedievalWeaponItem;

import net.minecraft.world.item.Item;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.extensions.common.RegisterClientExtensionsEvent;

import java.util.ArrayList;
import java.util.List;

/**
 * 클라이언트에서만 필요한 설정을 붙인다.
 *
 * <p>이 모드의 무기 전부에 {@link MedievalWeaponClientExtensions}를 연결한다.
 * 1인칭 휘두르기와 3인칭 자세가 거기 들어 있다.
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
    }
}
