package com.dykng.medievalarms.weapon;

import net.minecraft.world.item.Item;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.Tier;
import net.minecraft.world.item.Tiers;

/**
 * ★ 무기 스펙 표. 이 모드에서 가장 자주 손대게 될 파일이다.
 *
 * <p>상수 하나가 무기 하나다. 여기에 줄을 추가하고
 * {@code src/main/resources/assets/medievalarms/textures/item/<id>.png} 를 넣으면
 * 등록·모델·레시피·번역·모션이 전부 자동으로 따라온다. 다른 파일은 건드릴 필요가 없다.
 *
 * <p><b>공격속도(attackSpeed)에 대해:</b> 플레이어의 기본 공격속도는 4.0이다.
 * 여기 적는 값은 거기서 <i>빼는</i> 양이라 항상 음수다.
 * 예를 들어 -2.9를 적으면 실제 공격속도는 4.0 - 2.9 = 1.1회/초가 된다.
 * 참고로 바닐라 철검은 -2.4(=1.6회/초), 다이아 도끼는 -3.0(=1.0회/초)이다.
 *
 * <p><b>공격력(attackDamage)에 대해:</b> 여기 적는 값에 티어 보너스가 더해진다.
 * 철 티어는 +2, 다이아 티어는 +3이다. 그리고 맨손 기본 1이 또 더해진다.
 * 즉 철 티어에 4를 적으면 툴팁에는 1 + 4 + 2 = 7이 뜬다.
 */
public enum WeaponType {

    //   식별자          티어             공격력  공격속도  리치보너스  모션
    SPEAR("spear", Tiers.IRON, 4, -2.9F, 1.5D, SwingMotion.THRUST),
    HALBERD("halberd", Tiers.IRON, 6, -3.2F, 2.0D, SwingMotion.SWEEP),
    MACE("mace", Tiers.IRON, 6, -3.1F, 0.0D, SwingMotion.OVERHEAD),
    BATTLEAXE("battleaxe", Tiers.IRON, 7, -3.1F, 0.0D, SwingMotion.CHOP),
    WARHAMMER("warhammer", Tiers.DIAMOND, 8, -3.3F, 0.0D, SwingMotion.OVERHEAD),
    LONGSWORD("longsword", Tiers.DIAMOND, 6, -2.6F, 0.5D, SwingMotion.SLASH);

    /** 아이템 ID. {@code medievalarms:spear} 의 뒷부분이자 텍스처 파일 이름이다. */
    public final String id;
    /** 내구도·채굴속도·인챈트 수용도·수리 재료를 한꺼번에 정하는 등급. */
    public final Tier tier;
    /** 티어 보너스를 뺀 순수 공격력. 위 클래스 주석 참고. */
    public final int attackDamage;
    /** 기본 공격속도 4.0에서 빼는 값. 항상 음수. */
    public final float attackSpeed;
    /** 닿는 거리 보너스(블록 단위). 0이면 보너스 없음. 창 계열에서 쓴다. */
    public final double reachBonus;
    /** 휘두를 때의 동작. {@link SwingMotion} 참고. */
    public final SwingMotion motion;

    WeaponType(String id, Tier tier, int attackDamage, float attackSpeed, double reachBonus, SwingMotion motion) {
        this.id = id;
        this.tier = tier;
        this.attackDamage = attackDamage;
        this.attackSpeed = attackSpeed;
        this.reachBonus = reachBonus;
        this.motion = motion;
    }

    /**
     * 제작·수리에 쓰는 주 재료. 티어에서 그대로 따온다.
     * 레시피 생성기가 이 값을 쓴다.
     */
    public Item craftingMaterial() {
        return this.tier == Tiers.DIAMOND ? Items.DIAMOND : Items.IRON_INGOT;
    }

    /** 게임에 표시될 한국어 이름. 번역 파일 생성기가 쓴다. */
    public String koreanName() {
        return switch (this) {
            case SPEAR -> "창";
            case HALBERD -> "미늘창";
            case MACE -> "철퇴";
            case BATTLEAXE -> "전투도끼";
            case WARHAMMER -> "워해머";
            case LONGSWORD -> "장검";
        };
    }

    /** 게임에 표시될 영어 이름. "battleaxe" -> "Battleaxe" 처럼 첫 글자만 대문자로. */
    public String englishName() {
        return Character.toUpperCase(this.id.charAt(0)) + this.id.substring(1);
    }
}
