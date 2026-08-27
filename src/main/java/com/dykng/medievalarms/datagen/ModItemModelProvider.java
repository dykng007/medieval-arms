package com.dykng.medievalarms.datagen;

import com.dykng.medievalarms.MedievalArms;
import com.dykng.medievalarms.armor.ArmorSet;
import com.dykng.medievalarms.registry.ModItems;
import com.dykng.medievalarms.weapon.WeaponType;

import net.minecraft.data.PackOutput;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.neoforge.client.model.generators.ItemModelBuilder;
import net.neoforged.neoforge.client.model.generators.ItemModelProvider;
import net.minecraft.world.item.ItemDisplayContext;
import net.neoforged.neoforge.common.data.ExistingFileHelper;

/**
 * 아이템이 화면에 어떻게 보일지 정하는 모델 JSON을 만든다.
 *
 * <p>결과물은 {@code src/generated/resources/assets/medievalarms/models/item/} 에 나온다.
 * 손으로 JSON을 쓰지 않아도 되도록 이 클래스가 대신 써준다.
 */
public class ModItemModelProvider extends ItemModelProvider {

    /**
     * 손을 자루 끝 쪽으로 얼마나 내려 잡게 할지.
     *
     * <p>무기가 클수록 더 많이 밀어야 자루 끝을 쥔 모습이 된다.
     * 키우면 자루 끝에 더 가까이 잡고, 너무 키우면 손이 자루 밖으로 나가
     * 무기가 허공에 떠 보인다.
     */
    private static final float GRIP_FACTOR = 3.2F;

    public ModItemModelProvider(PackOutput output, ExistingFileHelper existingFileHelper) {
        super(output, MedievalArms.MOD_ID, existingFileHelper);
    }

    @Override
    protected void registerModels() {
        for (WeaponType type : WeaponType.values()) {
            weapon(type);
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

    /**
     * 무기 모델을 만든다.
     *
     * <p>부모는 바닐라 {@code item/handheld} 다. 기본값인 {@code generated} 를 쓰면
     * 아이템이 손에서 납작하게 들려 이상하다.
     *
     * <p>그 위에 손에 들었을 때의 크기와 위치를 무기마다 덮어쓴다.
     * 아이콘은 32x32 안에 대각선으로 꽉 차 있어서 그림만으로는 자루를 더 늘릴 수 없다.
     * 창이나 미늘창을 바닐라 검과 같은 크기로 들면 자루가 어정쩡하게 짧아 보인다.
     * 그래서 손에 들었을 때만 통째로 키운다. 인벤토리 아이콘 크기는 그대로다.
     */
    private void weapon(WeaponType type) {
        ItemModelBuilder model = withExistingParent(type.id, mcLoc("item/handheld"))
                .texture("layer0", itemTexture(type.id));

        float scale = type.handScale;
        if (scale == 1.0F) {
            return;     // 바닐라 기본값 그대로 쓴다
        }

        // 아래 숫자들은 바닐라 item/handheld.json 의 값에서 출발한 것이다.
        //   3인칭  회전 (0,-90,55)  이동 (0, 4.0, 0.5)    크기 0.85
        //   1인칭  회전 (0,-90,25)  이동 (1.13, 3.2, 1.13) 크기 0.68
        //
        // 크기만 키우면 무기가 손을 중심으로 커져서, 손이 자루 한가운데를 잡은
        // 모습이 된다. 장병기는 자루 끝을 잡아야 하므로 무기를 위로 밀어올린다.
        // 그러면 손 위치에 오는 부분이 무기의 아래쪽, 즉 자루 끝이 된다.
        //
        // 처음에는 반대로 빼서 무기를 내렸는데, 그러면 손이 오히려 날 쪽으로
        // 올라가 자루 한가운데를 쥔 모습이 됐다.
        float grip = (scale - 1.0F) * GRIP_FACTOR;

        applyHand(model, ItemDisplayContext.THIRD_PERSON_RIGHT_HAND,
                0, -90, 55, 0, 4.0F + grip, 0.5F, 0.85F * scale);
        applyHand(model, ItemDisplayContext.THIRD_PERSON_LEFT_HAND,
                0, 90, -55, 0, 4.0F + grip, 0.5F, 0.85F * scale);
        applyHand(model, ItemDisplayContext.FIRST_PERSON_RIGHT_HAND,
                0, -90, 25, 1.13F, 3.2F + grip, 1.13F, 0.68F * scale);
        applyHand(model, ItemDisplayContext.FIRST_PERSON_LEFT_HAND,
                0, 90, -25, 1.13F, 3.2F + grip, 1.13F, 0.68F * scale);

        // 땅에 떨어졌을 때도 같은 비율로 키워 어색하지 않게 한다.
        model.transforms().transform(ItemDisplayContext.GROUND)
                .rotation(0, 0, 0).translation(0, 2, 0).scale(0.5F * scale).end();
    }

    private void applyHand(ItemModelBuilder model, ItemDisplayContext context,
                           float rx, float ry, float rz,
                           float tx, float ty, float tz, float scale) {
        model.transforms()
                .transform(context)
                .rotation(rx, ry, rz)
                .translation(tx, ty, tz)
                .scale(scale)
                .end();
    }

    /** {@code medievalarms:item/<name>} — 텍스처 png의 위치. */
    private ResourceLocation itemTexture(String name) {
        return ResourceLocation.fromNamespaceAndPath(MedievalArms.MOD_ID, "item/" + name);
    }
}
