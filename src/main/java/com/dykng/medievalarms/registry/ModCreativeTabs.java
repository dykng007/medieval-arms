package com.dykng.medievalarms.registry;

import com.dykng.medievalarms.MedievalArms;
import com.dykng.medievalarms.weapon.WeaponType;

import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * 크리에이티브 모드 인벤토리에 이 모드 전용 탭을 하나 만든다.
 * 탭 아이콘은 장검이고, 안에는 {@link ModItems}에 등록된 순서대로 전부 들어간다.
 */
public final class ModCreativeTabs {

    public static final DeferredRegister<CreativeModeTab> TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, MedievalArms.MOD_ID);

    public static final DeferredHolder<CreativeModeTab, CreativeModeTab> MAIN = TABS.register(
            "main",
            () -> CreativeModeTab.builder()
                    // 탭 이름은 번역 키로 둔다. 실제 글자는 lang 파일에서 온다.
                    .title(Component.translatable("itemGroup.medievalarms.main"))
                    .icon(() -> new ItemStack(ModItems.weapon(WeaponType.LONGSWORD).get()))
                    .displayItems((params, output) -> {
                        for (var item : ModItems.all()) {
                            output.accept(item.get());
                        }
                    })
                    .build());

    private ModCreativeTabs() {
    }
}
