package com.dykng.medievalarms.datagen;

import com.dykng.medievalarms.MedievalArms;
import com.dykng.medievalarms.armor.ArmorSet;
import com.dykng.medievalarms.registry.ModItems;
import com.dykng.medievalarms.weapon.WeaponType;

import net.minecraft.data.PackOutput;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.neoforge.client.model.generators.ItemModelProvider;
import net.neoforged.neoforge.common.data.ExistingFileHelper;

/**
 * 아이템이 화면에 어떻게 보일지 정하는 모델 JSON을 만든다.
 *
 * <p>결과물은 {@code src/generated/resources/assets/medievalarms/models/item/} 에 나온다.
 * 손으로 JSON을 쓰지 않아도 되도록 이 클래스가 대신 써준다.
 */
public class ModItemModelProvider extends ItemModelProvider {

    public ModItemModelProvider(PackOutput output, ExistingFileHelper existingFileHelper) {
        super(output, MedievalArms.MOD_ID, existingFileHelper);
    }

    @Override
    protected void registerModels() {
        // 무기는 "handheld" 부모를 쓴다.
        // 기본값인 "generated"를 쓰면 아이템이 손에서 납작하게 들려 이상하다.
        // handheld는 바닐라 검·도끼가 쓰는 것으로, 손에 비스듬히 쥔 모양으로 그려준다.
        for (WeaponType type : WeaponType.values()) {
            handheld(type.id);
        }

        // 갑옷은 손에 쥐는 물건이 아니므로 평면인 "generated"가 맞다.
        for (ArmorSet set : ArmorSet.values()) {
            for (var piece : ModItems.ARMOR_PIECES) {
                // basicItem은 넘겨준 경로에 "item/"을 스스로 붙인다.
                // 그래서 여기서는 접두사 없이 아이템 이름만 넘겨야 한다.
                basicItem(ResourceLocation.fromNamespaceAndPath(
                        MedievalArms.MOD_ID, set.id + "_" + piece.getName()));
            }
        }
    }

    private void handheld(String name) {
        withExistingParent(name, mcLoc("item/handheld"))
                .texture("layer0", itemTexture(name));
    }

    /** {@code medievalarms:item/<name>} — 텍스처 png의 위치. */
    private ResourceLocation itemTexture(String name) {
        return ResourceLocation.fromNamespaceAndPath(MedievalArms.MOD_ID, "item/" + name);
    }
}
