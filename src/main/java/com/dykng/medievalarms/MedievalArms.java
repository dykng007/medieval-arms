package com.dykng.medievalarms;

import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.ModContainer;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

/**
 * 모드의 진입점.
 *
 * <p>NeoForge는 {@code @Mod} 애노테이션이 붙은 클래스를 찾아, 아래 생성자를 딱 한 번 호출한다.
 * 생성자에서 하는 일은 "등록기(DeferredRegister)들을 이벤트 버스에 연결"하는 것뿐이다.
 * 실제 아이템 목록 같은 내용물은 각 registry 클래스가 들고 있다.
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
        LOGGER.info("Medieval Arms 로딩 시작");
        // 콘텐츠 등록은 M1에서 여기에 연결한다.
    }
}
