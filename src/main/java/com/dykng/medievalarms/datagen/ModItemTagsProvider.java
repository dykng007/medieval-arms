package com.dykng.medievalarms.datagen;

import com.dykng.medievalarms.MedievalArms;
import com.dykng.medievalarms.armor.ArmorSet;
import com.dykng.medievalarms.registry.ModItems;
import com.dykng.medievalarms.weapon.WeaponType;

import net.minecraft.core.HolderLookup;
import net.minecraft.data.PackOutput;
import net.minecraft.data.tags.ItemTagsProvider;
import net.minecraft.data.tags.TagsProvider;
import net.minecraft.tags.ItemTags;
import net.minecraft.world.item.ArmorItem;
import net.neoforged.neoforge.common.Tags;
import net.neoforged.neoforge.common.data.ExistingFileHelper;

import java.util.concurrent.CompletableFuture;

/**
 * 아이템 태그를 붙인다.
 *
 * <p>태그는 "이 아이템은 어떤 부류인가"를 게임에 알려주는 이름표다. 붙이지 않으면
 * 겉보기엔 멀쩡한데 인챈트가 안 걸리고, 모루 수리가 안 되고, 다른 모드가 이 무기를
 * 무기로 인식하지 못한다. 사실상 필수다.
 */
public class ModItemTagsProvider extends ItemTagsProvider {

    public ModItemTagsProvider(PackOutput output,
                               CompletableFuture<HolderLookup.Provider> lookup,
                               ExistingFileHelper existingFileHelper) {
        // 세 번째 인자는 "블록 태그를 아이템 태그로 복사"할 때 쓰는 것인데
        // 이 모드는 블록이 없으므로 빈 것을 넘긴다.
        super(output, lookup, CompletableFuture.completedFuture(TagsProvider.TagLookup.empty()));
    }

    @Override
    protected void addTags(HolderLookup.Provider provider) {
        for (WeaponType type : WeaponType.values()) {
            var item = ModItems.weapon(type).get();

            // 무기 인챈트(날카로움, 강타 등)를 걸 수 있게 한다.
            tag(ItemTags.SWORD_ENCHANTABLE).add(item);
            // 내구성·수선 같은 도구 공용 인챈트.
            tag(ItemTags.DURABILITY_ENCHANTABLE).add(item);
            // 근접 무기 공용 인챈트 대상.
            tag(ItemTags.WEAPON_ENCHANTABLE).add(item);
            // 다른 모드가 "이건 근접 무기다"라고 인식하는 공통 태그.
            tag(Tags.Items.MELEE_WEAPON_TOOLS).add(item);
            tag(Tags.Items.TOOLS).add(item);
        }

        for (ArmorSet set : ArmorSet.values()) {
            for (ArmorItem.Type piece : ModItems.ARMOR_PIECES) {
                var item = ModItems.armor(set, piece).get();

                // 보호 등 갑옷 인챈트.
                tag(ItemTags.ARMOR_ENCHANTABLE).add(item);
                tag(ItemTags.DURABILITY_ENCHANTABLE).add(item);

                // 부위별 착용 슬롯 태그. 이게 있어야 우클릭으로 바로 입어진다.
                switch (piece) {
                    case HELMET -> tag(ItemTags.HEAD_ARMOR).add(item);
                    case CHESTPLATE -> tag(ItemTags.CHEST_ARMOR).add(item);
                    case LEGGINGS -> tag(ItemTags.LEG_ARMOR).add(item);
                    case BOOTS -> tag(ItemTags.FOOT_ARMOR).add(item);
                    default -> {
                        // BODY(늑대 갑옷)는 이 모드에서 만들지 않는다.
                    }
                }
            }
        }
    }

    @Override
    public String getName() {
        return MedievalArms.MOD_ID + " item tags";
    }
}
