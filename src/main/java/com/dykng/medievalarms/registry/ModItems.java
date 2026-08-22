package com.dykng.medievalarms.registry;

import com.dykng.medievalarms.MedievalArms;
import com.dykng.medievalarms.armor.ArmorSet;
import com.dykng.medievalarms.weapon.MedievalWeaponItem;
import com.dykng.medievalarms.weapon.WeaponType;

import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.Item;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

import java.util.ArrayList;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;

/**
 * 이 모드의 모든 아이템을 등록한다.
 *
 * <p>아이템 목록을 여기에 손으로 나열하지 않는다. {@link WeaponType}과 {@link ArmorSet}을
 * 순회하면서 자동으로 만들어낸다. 그래서 무기나 갑옷을 추가할 때 이 파일은 건드릴 일이 없다.
 */
public final class ModItems {

    public static final DeferredRegister.Items ITEMS =
            DeferredRegister.createItems(MedievalArms.MOD_ID);

    /** 무기 종류 -> 등록된 아이템. */
    private static final Map<WeaponType, DeferredItem<MedievalWeaponItem>> WEAPONS =
            new EnumMap<>(WeaponType.class);

    /** 갑옷 세트 + 부위 -> 등록된 아이템. */
    private static final Map<ArmorSet, Map<ArmorItem.Type, DeferredItem<ArmorItem>>> ARMOR =
            new EnumMap<>(ArmorSet.class);

    /** 크리에이티브 탭에 넣을 순서대로 모아둔 전체 목록. */
    private static final List<DeferredItem<? extends Item>> ALL = new ArrayList<>();

    /**
     * 이 모드가 만드는 갑옷 부위.
     * {@code ArmorItem.Type}에는 늑대 갑옷용 BODY도 있지만 사람이 입는 네 부위만 쓴다.
     */
    public static final ArmorItem.Type[] ARMOR_PIECES = {
            ArmorItem.Type.HELMET,
            ArmorItem.Type.CHESTPLATE,
            ArmorItem.Type.LEGGINGS,
            ArmorItem.Type.BOOTS,
    };

    static {
        // ── 무기 ──
        for (WeaponType type : WeaponType.values()) {
            DeferredItem<MedievalWeaponItem> item =
                    ITEMS.register(type.id, () -> new MedievalWeaponItem(type));
            WEAPONS.put(type, item);
            ALL.add(item);
        }

        // ── 갑옷 ──
        for (ArmorSet set : ArmorSet.values()) {
            Map<ArmorItem.Type, DeferredItem<ArmorItem>> pieces = new EnumMap<>(ArmorItem.Type.class);
            for (ArmorItem.Type type : ARMOR_PIECES) {
                // 아이템 ID는 "squire_helmet" 형태가 된다.
                String name = set.id + "_" + type.getName();
                DeferredItem<ArmorItem> item = ITEMS.register(name, () -> new ArmorItem(
                        ModArmorMaterials.get(set),
                        type,
                        // 내구도는 부위별 기본값에 세트 배수를 곱한 값이다.
                        // 예: 흉갑 기본 16 x 종자 배수 15 = 240
                        new Item.Properties().durability(type.getDurability(set.durabilityMultiplier))));
                pieces.put(type, item);
                ALL.add(item);
            }
            ARMOR.put(set, pieces);
        }
    }

    private ModItems() {
    }

    public static DeferredItem<MedievalWeaponItem> weapon(WeaponType type) {
        return WEAPONS.get(type);
    }

    public static DeferredItem<ArmorItem> armor(ArmorSet set, ArmorItem.Type piece) {
        return ARMOR.get(set).get(piece);
    }

    /** 등록된 모든 아이템. 크리에이티브 탭과 데이터 생성기가 순회할 때 쓴다. */
    public static List<DeferredItem<? extends Item>> all() {
        return List.copyOf(ALL);
    }
}
