package com.dykng.medievalarms.datagen;

import com.dykng.medievalarms.MedievalArms;

import net.minecraft.core.HolderLookup;
import net.minecraft.data.DataGenerator;
import net.minecraft.data.PackOutput;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.data.event.GatherDataEvent;

import java.util.concurrent.CompletableFuture;

/**
 * {@code ./gradlew runData} 를 실행하면 여기가 호출된다.
 *
 * <p>각 provider가 만들어낸 JSON은 {@code src/generated/resources/} 에 나오고,
 * 그 폴더는 커밋 대상이다. 그래야 CI에서 runData를 돌리지 않아도 빌드가 된다.
 *
 * <p>무기나 갑옷을 추가·수정한 뒤에는 반드시 {@code runData}를 다시 돌려야 한다.
 * 그러지 않으면 새 아이템의 모델·레시피·이름이 없어 게임에서 보라-검정 체크무늬로 뜬다.
 */
@EventBusSubscriber(modid = MedievalArms.MOD_ID, bus = EventBusSubscriber.Bus.MOD)
public class DataGenerators {

    @SubscribeEvent
    public static void gatherData(GatherDataEvent event) {
        DataGenerator generator = event.getGenerator();
        PackOutput output = generator.getPackOutput();
        CompletableFuture<HolderLookup.Provider> lookup = event.getLookupProvider();

        // 클라이언트 리소스: 보이는 것
        generator.addProvider(event.includeClient(),
                new ModItemModelProvider(output, event.getExistingFileHelper()));
        generator.addProvider(event.includeClient(),
                new ModLanguageProvider(output, false));   // en_us
        generator.addProvider(event.includeClient(),
                new ModLanguageProvider(output, true));    // ko_kr

        // 서버 데이터: 규칙에 해당하는 것
        generator.addProvider(event.includeServer(),
                new ModRecipeProvider(output, lookup));
        generator.addProvider(event.includeServer(),
                new ModItemTagsProvider(output, lookup, event.getExistingFileHelper()));
    }
}
