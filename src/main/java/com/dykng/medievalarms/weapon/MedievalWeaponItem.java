package com.dykng.medievalarms.weapon;

import com.dykng.medievalarms.MedievalArms;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.EquipmentSlotGroup;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.item.component.ItemAttributeModifiers;

/**
 * 이 모드의 모든 근접 무기가 쓰는 단 하나의 아이템 클래스.
 *
 * <p>무기마다 클래스를 따로 만들지 않는다. 무기별 차이는 전부 {@link WeaponType} 값에서 오고,
 * 이 클래스는 그 값을 읽어 동작할 뿐이다. 그래서 무기를 추가할 때 자바 파일을 새로 만들 필요가 없다.
 *
 * <p>{@link SwordItem}을 상속하는 이유는 검이라서가 아니라, 거미줄을 빠르게 자르고
 * 몹을 때렸을 때 내구도가 1만 닳는 등 "근접 무기다운" 동작이 이미 들어 있기 때문이다.
 */
public class MedievalWeaponItem extends SwordItem {

    private final WeaponType type;

    public MedievalWeaponItem(WeaponType type) {
        super(type.tier, new Item.Properties().attributes(buildAttributes(type)));
        this.type = type;
    }

    public WeaponType getWeaponType() {
        return this.type;
    }

    /**
     * 공격력·공격속도·리치를 아이템 속성으로 만든다.
     *
     * <p>{@code SwordItem.createAttributes()}를 그냥 쓰지 않고 직접 조립하는 이유는
     * 리치 보너스(ENTITY_INTERACTION_RANGE)를 얹어야 하기 때문이다. 바닐라 헬퍼는
     * 공격력과 공격속도 두 개만 넣어주고 그 결과에 나중에 추가할 방법이 없다.
     */
    private static ItemAttributeModifiers buildAttributes(WeaponType type) {
        ItemAttributeModifiers.Builder builder = ItemAttributeModifiers.builder()
                .add(
                        Attributes.ATTACK_DAMAGE,
                        new AttributeModifier(
                                BASE_ATTACK_DAMAGE_ID,
                                type.attackDamage + type.tier.getAttackDamageBonus(),
                                AttributeModifier.Operation.ADD_VALUE),
                        EquipmentSlotGroup.MAINHAND)
                .add(
                        Attributes.ATTACK_SPEED,
                        new AttributeModifier(
                                BASE_ATTACK_SPEED_ID,
                                type.attackSpeed,
                                AttributeModifier.Operation.ADD_VALUE),
                        EquipmentSlotGroup.MAINHAND);

        // 리치 보너스는 값이 있을 때만 붙인다.
        // 0짜리 수정자를 달아두면 툴팁에 "+0 거리" 같은 무의미한 줄이 뜬다.
        if (type.reachBonus != 0.0D) {
            builder.add(
                    Attributes.ENTITY_INTERACTION_RANGE,
                    new AttributeModifier(
                            ResourceLocation.fromNamespaceAndPath(MedievalArms.MOD_ID, "weapon_reach"),
                            type.reachBonus,
                            AttributeModifier.Operation.ADD_VALUE),
                    EquipmentSlotGroup.MAINHAND);
        }

        return builder.build();
    }
}
