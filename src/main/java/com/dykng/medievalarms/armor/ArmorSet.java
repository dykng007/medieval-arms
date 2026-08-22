package com.dykng.medievalarms.armor;

import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Items;

/**
 * ★ 갑옷 세트 표. {@link com.dykng.medievalarms.weapon.WeaponType}의 갑옷 버전이다.
 *
 * <p>세트를 추가하려면 여기에 상수를 하나 더하고, 부위별 아이템 텍스처 4장과
 * 착용 레이어 텍스처 2장을 넣으면 된다. 파일 이름 규칙은 아래와 같다.
 *
 * <pre>
 * textures/item/&lt;id&gt;_helmet.png       (그리고 _chestplate, _leggings, _boots)
 * textures/models/armor/&lt;id&gt;_layer_1.png   몸에 입었을 때 보이는 그림
 * textures/models/armor/&lt;id&gt;_layer_2.png   각반(다리) 부분
 * </pre>
 *
 * <p><b>방어력 수치 참고:</b> 바닐라 철 갑옷은 2/6/5/2(투구/흉갑/각반/부츠)로 합계 15,
 * 다이아 갑옷은 3/8/6/3으로 합계 20이다. 아래 값은 그에 맞춰 잡았다.
 */
public enum ArmorSet {

    /** 종자 갑옷 — 철 급. 바닐라 철 갑옷과 비슷하되 아주 약간 튼튼하다. */
    SQUIRE("squire", "종자", "Squire",
            2, 6, 5, 2,
            15,     // 내구도 배수. 바닐라 철도 15다.
            9,      // 인챈트 수용도. 바닐라 철은 9.
            0.0F,   // 강인함
            0.0F,   // 넉백 저항
            Items.IRON_INGOT),

    /** 기사 갑옷 — 다이아 급. 넉백 저항이 조금 붙어 밀리지 않고 버틴다. */
    KNIGHT("knight", "기사", "Knight",
            3, 8, 6, 3,
            33,     // 바닐라 다이아와 동일
            10,     // 바닐라 다이아와 동일
            2.0F,   // 바닐라 다이아와 동일
            0.1F,   // 중갑옷다운 넉백 저항 (바닐라 네더라이트가 0.1)
            Items.DIAMOND);

    public final String id;
    public final String koreanName;
    public final String englishName;
    public final int helmetDefense;
    public final int chestplateDefense;
    public final int leggingsDefense;
    public final int bootsDefense;
    /** 내구도 배수. 부위별 기본값에 곱해진다. */
    public final int durabilityMultiplier;
    public final int enchantmentValue;
    public final float toughness;
    public final float knockbackResistance;
    /** 수리 재료이자 제작 재료. */
    public final Item material;

    ArmorSet(String id, String koreanName, String englishName,
             int helmetDefense, int chestplateDefense, int leggingsDefense, int bootsDefense,
             int durabilityMultiplier, int enchantmentValue,
             float toughness, float knockbackResistance, Item material) {
        this.id = id;
        this.koreanName = koreanName;
        this.englishName = englishName;
        this.helmetDefense = helmetDefense;
        this.chestplateDefense = chestplateDefense;
        this.leggingsDefense = leggingsDefense;
        this.bootsDefense = bootsDefense;
        this.durabilityMultiplier = durabilityMultiplier;
        this.enchantmentValue = enchantmentValue;
        this.toughness = toughness;
        this.knockbackResistance = knockbackResistance;
        this.material = material;
    }

    /** 부위별 방어력. 위에 나열한 네 값 중 해당하는 것을 꺼낸다. */
    public int defenseFor(ArmorItem.Type type) {
        return switch (type) {
            case HELMET -> this.helmetDefense;
            case CHESTPLATE -> this.chestplateDefense;
            case LEGGINGS -> this.leggingsDefense;
            case BOOTS -> this.bootsDefense;
            // BODY는 늑대 갑옷 같은 동물용 슬롯이라 이 모드에서는 쓰지 않는다.
            default -> 0;
        };
    }

    /** 부위 이름의 한국어. "종자 흉갑" 처럼 조합해 쓴다. */
    public static String koreanPieceName(ArmorItem.Type type) {
        return switch (type) {
            case HELMET -> "투구";
            case CHESTPLATE -> "흉갑";
            case LEGGINGS -> "각반";
            case BOOTS -> "장화";
            default -> type.getName();
        };
    }

    /** 부위 이름의 영어. "Squire Chestplate" 처럼 조합해 쓴다. */
    public static String englishPieceName(ArmorItem.Type type) {
        String name = type.getName();
        return Character.toUpperCase(name.charAt(0)) + name.substring(1);
    }
}
