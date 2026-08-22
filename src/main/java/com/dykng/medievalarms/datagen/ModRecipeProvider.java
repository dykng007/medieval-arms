package com.dykng.medievalarms.datagen;

import com.dykng.medievalarms.armor.ArmorSet;
import com.dykng.medievalarms.registry.ModItems;
import com.dykng.medievalarms.weapon.WeaponType;

import net.minecraft.core.HolderLookup;
import net.minecraft.data.PackOutput;
import net.minecraft.data.recipes.RecipeCategory;
import net.minecraft.data.recipes.RecipeOutput;
import net.minecraft.data.recipes.RecipeProvider;
import net.minecraft.data.recipes.ShapedRecipeBuilder;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Items;

import java.util.concurrent.CompletableFuture;

/**
 * 제작대 레시피를 만든다.
 *
 * <p><b>레시피 충돌에 대해 — 이 파일에서 가장 중요한 부분:</b>
 * 마인크래프트의 모양 있는(shaped) 레시피는 빈 줄과 빈 열을 잘라낸 뒤 비교한다.
 * 그래서 잘라낸 결과가 바닐라 레시피와 같아지면 둘 중 하나만 만들어지고
 * 나머지는 영원히 제작할 수 없게 된다. 게임은 경고도 주지 않는다.
 *
 * <p>실제로 처음 잡았던 배치 중 두 개가 여기 걸렸다.
 * 워해머의 {@code MMM / _S_ / _S_} 는 바닐라 곡괭이와 같았고,
 * 전투도끼의 {@code MM_ / MS_ / _S_} 는 잘라내면 바닐라 도끼와 같았다.
 * 아래 배치는 그 점을 확인해 잡은 것이다. 배치를 바꿀 때는 바닐라와 겹치지 않는지
 * 반드시 다시 확인해야 한다.
 *
 * <p>갑옷도 마찬가지 이유로 가운데에 가죽을 한 장 넣었다. 그러지 않으면
 * 철로 만드는 종자 갑옷이 바닐라 철 갑옷과, 다이아로 만드는 기사 갑옷이
 * 바닐라 다이아 갑옷과 정확히 같은 배치가 된다. 가죽 안감은 중세 갑옷답기도 하다.
 */
public class ModRecipeProvider extends RecipeProvider {

    public ModRecipeProvider(PackOutput output, CompletableFuture<HolderLookup.Provider> lookup) {
        super(output, lookup);
    }

    @Override
    protected void buildRecipes(RecipeOutput output) {
        for (WeaponType type : WeaponType.values()) {
            weaponRecipe(output, type);
        }
        for (ArmorSet set : ArmorSet.values()) {
            armorRecipes(output, set);
        }
    }

    /** M = 주 재료(철괴 또는 다이아), S = 막대기. */
    private void weaponRecipe(RecipeOutput output, WeaponType type) {
        String[] pattern = switch (type) {
            // 창 — 긴 자루 끝에 촉 하나. 대각선이라 잘라낼 여백이 없다.
            case SPEAR -> new String[]{"  M", " S ", "S  "};
            // 미늘창 — 촉 옆에 도끼날이 하나 더 붙는다.
            case HALBERD -> new String[]{" MM", " SM", "S  "};
            // 철퇴 — 좁고 뭉툭한 머리.
            case MACE -> new String[]{" M ", "MMM", " S "};
            // 전투도끼 — 자루 양옆으로 날. 바닐라 도끼와 겹치지 않게 가운데를 비웠다.
            case BATTLEAXE -> new String[]{"M M", "MSM", " S "};
            // 워해머 — 넓고 육중한 머리. 가운데 막대기가 바닐라 곡괭이와 구분해준다.
            case WARHAMMER -> new String[]{"MMM", "MSM", " S "};
            // 장검 — 검을 대각선으로 길게 늘인 모양.
            case LONGSWORD -> new String[]{"  M", " M ", "S  "};
        };

        Item material = type.craftingMaterial();
        ShapedRecipeBuilder builder = ShapedRecipeBuilder.shaped(RecipeCategory.COMBAT, ModItems.weapon(type).get());
        for (String row : pattern) {
            builder.pattern(row);
        }
        builder.define('M', material)
                .define('S', Items.STICK)
                // 레시피북 잠금 해제 조건. 없으면 레시피가 책에 영영 안 뜬다.
                .unlockedBy(getHasName(material), has(material))
                .save(output);
    }

    /** M = 주 재료, L = 가죽(안감). 가죽이 바닐라 갑옷 레시피와의 충돌을 막는다. */
    private void armorRecipes(RecipeOutput output, ArmorSet set) {
        record Shape(ArmorItem.Type piece, String[] rows) {
        }

        Shape[] shapes = {
                new Shape(ArmorItem.Type.HELMET, new String[]{"MMM", "MLM"}),
                new Shape(ArmorItem.Type.CHESTPLATE, new String[]{"M M", "MLM", "MMM"}),
                new Shape(ArmorItem.Type.LEGGINGS, new String[]{"MMM", "MLM", "M M"}),
                new Shape(ArmorItem.Type.BOOTS, new String[]{"M M", "MLM"}),
        };

        Item material = set.material;
        for (Shape shape : shapes) {
            ShapedRecipeBuilder builder =
                    ShapedRecipeBuilder.shaped(RecipeCategory.COMBAT, ModItems.armor(set, shape.piece()).get());
            for (String row : shape.rows()) {
                builder.pattern(row);
            }
            builder.define('M', material)
                    .define('L', Items.LEATHER)
                    .unlockedBy(getHasName(material), has(material))
                    .save(output);
        }
    }
}
