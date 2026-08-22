package com.dykng.medievalarms.datagen;

import com.dykng.medievalarms.MedievalArms;
import com.dykng.medievalarms.armor.ArmorSet;
import com.dykng.medievalarms.registry.ModItems;
import com.dykng.medievalarms.weapon.WeaponType;

import net.minecraft.data.PackOutput;
import net.minecraft.world.item.ArmorItem;
import net.neoforged.neoforge.common.data.LanguageProvider;

/**
 * 화면에 표시될 이름을 만든다. 영어와 한국어 두 벌.
 *
 * <p>이름을 자바 코드가 아니라 {@link WeaponType}과 {@link ArmorSet}에서 가져오기 때문에,
 * 무기를 추가하면 번역도 자동으로 따라온다.
 *
 * <p>한국어 파일은 {@code ko_kr}이다. 마인크래프트 언어 설정을 한국어로 두면 이 이름이 뜬다.
 */
public class ModLanguageProvider extends LanguageProvider {

    /** true면 한국어, false면 영어. */
    private final boolean korean;

    public ModLanguageProvider(PackOutput output, boolean korean) {
        super(output, MedievalArms.MOD_ID, korean ? "ko_kr" : "en_us");
        this.korean = korean;
    }

    @Override
    protected void addTranslations() {
        // 크리에이티브 탭 이름
        add("itemGroup.medievalarms.main", korean ? "중세 무기고" : "Medieval Arms");

        for (WeaponType type : WeaponType.values()) {
            add(ModItems.weapon(type).get(), korean ? type.koreanName() : type.englishName());
        }

        for (ArmorSet set : ArmorSet.values()) {
            for (ArmorItem.Type piece : ModItems.ARMOR_PIECES) {
                // 한국어는 "종자 투구", 영어는 "Squire Helmet"
                String name = korean
                        ? set.koreanName + " " + ArmorSet.koreanPieceName(piece)
                        : set.englishName + " " + ArmorSet.englishPieceName(piece);
                add(ModItems.armor(set, piece).get(), name);
            }
        }
    }
}
