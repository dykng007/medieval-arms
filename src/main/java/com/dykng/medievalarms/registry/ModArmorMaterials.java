package com.dykng.medievalarms.registry;

import com.dykng.medievalarms.MedievalArms;
import com.dykng.medievalarms.armor.ArmorSet;

import net.minecraft.core.Holder;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.crafting.Ingredient;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

import java.util.EnumMap;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * {@link ArmorSet}에 적힌 수치를 마인크래프트가 이해하는 {@code ArmorMaterial}로 등록한다.
 *
 * <p>갑옷 재질은 아이템과 별개의 레지스트리에 들어간다. 아이템이 "이 갑옷은 어떤 재질인가"를
 * 가리킬 때 여기 등록된 것을 참조한다. 세트를 추가하려면 {@link ArmorSet}에만 손대면 되고
 * 이 파일은 자동으로 따라온다.
 */
public final class ModArmorMaterials {

    public static final DeferredRegister<ArmorMaterial> ARMOR_MATERIALS =
            DeferredRegister.create(Registries.ARMOR_MATERIAL, MedievalArms.MOD_ID);

    /** 세트 -> 등록된 재질. 아이템을 만들 때 여기서 꺼내 쓴다. */
    private static final Map<ArmorSet, DeferredHolder<ArmorMaterial, ArmorMaterial>> BY_SET = new HashMap<>();

    static {
        for (ArmorSet set : ArmorSet.values()) {
            BY_SET.put(set, ARMOR_MATERIALS.register(set.id, () -> create(set)));
        }
    }

    private ModArmorMaterials() {
    }

    /** 해당 세트의 재질. {@code ArmorItem} 생성자에 그대로 넘긴다. */
    public static Holder<ArmorMaterial> get(ArmorSet set) {
        return BY_SET.get(set);
    }

    private static ArmorMaterial create(ArmorSet set) {
        // 부위별 방어력 표
        Map<ArmorItem.Type, Integer> defense = new EnumMap<>(ArmorItem.Type.class);
        for (ArmorItem.Type type : ArmorItem.Type.values()) {
            defense.put(type, set.defenseFor(type));
        }

        // 착용했을 때 몸에 그려질 텍스처의 위치.
        // ResourceLocation의 경로가 "squire"면 실제로 읽는 파일은
        //   assets/medievalarms/textures/models/armor/squire_layer_1.png (겉)
        //   assets/medievalarms/textures/models/armor/squire_layer_2.png (각반)
        // 이다. 이 규칙은 마인크래프트가 정해둔 것이라 파일 이름을 바꾸면 안 된다.
        List<ArmorMaterial.Layer> layers = List.of(
                new ArmorMaterial.Layer(ResourceLocation.fromNamespaceAndPath(MedievalArms.MOD_ID, set.id)));

        return new ArmorMaterial(
                defense,
                set.enchantmentValue,
                set.material == Items.DIAMOND ? SoundEvents.ARMOR_EQUIP_DIAMOND : SoundEvents.ARMOR_EQUIP_IRON,
                () -> Ingredient.of(set.material),
                layers,
                set.toughness,
                set.knockbackResistance);
    }
}
