package com.dykng.medievalarms;

import com.dykng.medievalarms.registry.ModArmorMaterials;
import com.dykng.medievalarms.registry.ModCreativeTabs;
import com.dykng.medievalarms.registry.ModItems;

import com.mojang.logging.LogUtils;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;
import org.slf4j.Logger;

/**
 * 모드의 진입점.
 *
 * <p>NeoForge는 {@code @Mod} 애노테이션이 붙은 이 클래스를 찾아 생성자를 딱 한 번 호출한다.
 * 생성자가 하는 일은 각 등록기를 이벤트 버스에 연결하는 것뿐이다. 실제 내용물은
 * {@code registry} 패키지의 클래스들이 들고 있다.
 *
 * <p>등록기를 버스에 붙여두면, NeoForge가 적절한 시점에 "이제 아이템을 등록하라"는 이벤트를
 * 쏘고 등록기가 알아서 반응한다. 그래서 여기서 등록 순서를 신경 쓸 필요가 없다.
 */
@Mod(MedievalArms.MOD_ID)
public class MedievalArms {

    /**
     * 모드 식별자. gradle.properties의 {@code mod_id}와 반드시 같아야 한다.
     * 아이템 ID가 {@code medievalarms:spear} 처럼 이 값으로 시작하게 된다.
     */
    public static final String MOD_ID = "medievalarms";

    private static final Logger LOGGER = LogUtils.getLogger();

    public MedievalArms(IEventBus modEventBus, ModContainer modContainer) {
        ModArmorMaterials.ARMOR_MATERIALS.register(modEventBus);
        ModItems.ITEMS.register(modEventBus);
        ModCreativeTabs.TABS.register(modEventBus);

        LOGGER.info("Medieval Arms: 아이템 {}개 등록 예약됨", ModItems.all().size());
    }
}
