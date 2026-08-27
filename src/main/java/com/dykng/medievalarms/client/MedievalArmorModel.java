package com.dykng.medievalarms.client;

import com.dykng.medievalarms.MedievalArms;

import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeDeformation;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.model.geom.builders.PartDefinition;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.LivingEntity;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.api.distmarker.OnlyIn;

/**
 * 갑옷을 그릴 때 쓰는 모델. 바닐라 사람 모델에 큐브를 몇 개 더 얹은 것이다.
 *
 * <p><b>왜 텍스처로는 안 되는가:</b> 마인크래프트 갑옷은 플레이어 모델 위에 씌우는
 * 상자다. 투구는 머리 큐브 하나, 흉갑은 몸통 큐브 하나뿐이라, 텍스처를 아무리
 * 정교하게 그려도 실루엣은 상자 그대로다. 바닐라 투구가 각져 보이는 것도 같은 이유다.
 *
 * <p>모양을 바꾸려면 모델을 바꿔야 한다. NeoForge 가
 * {@code IClientItemExtensions#getHumanoidArmorModel} 로 그 자리를 열어준다.
 *
 * <p><b>투구에 더한 것:</b>
 * <ul>
 *   <li>정수리에 좁은 돔 큐브 — 위로 갈수록 좁아져 항아리를 엎어놓은 윤곽이 된다</li>
 *   <li>얼굴 앞에 바이저 큐브 — 앞으로 튀어나와 평평한 면이 깨진다</li>
 *   <li>턱 밑에 테두리 큐브 — 아래가 살짝 벌어져 투구가 머리에 얹힌 것처럼 보인다</li>
 * </ul>
 *
 * <p>추가 큐브의 UV 는 텍스처의 오른쪽 위 구역(가로 32~64, 세로 0~16)을 쓴다.
 * 그 자리는 원래 hat 칸인데 이 모드는 비워두므로 그대로 가져다 쓴다.
 */
@OnlyIn(Dist.CLIENT)
public class MedievalArmorModel extends HumanoidModel<LivingEntity> {

    /** 투구용 모델. 머리에만 큐브가 더 붙는다. */
    public static final ModelLayerLocation HELMET = new ModelLayerLocation(
            ResourceLocation.fromNamespaceAndPath(MedievalArms.MOD_ID, "armor_helmet"), "main");

    /** 흉갑용 모델. 어깨에 견갑이 붙는다. */
    public static final ModelLayerLocation CHESTPLATE = new ModelLayerLocation(
            ResourceLocation.fromNamespaceAndPath(MedievalArms.MOD_ID, "armor_chestplate"), "main");

    /**
     * 갑옷이 몸보다 살짝 커야 안쪽 살이 비쳐 보이지 않는다.
     * 바닐라도 겉 갑옷에 1.0, 속 갑옷(각반)에 0.5 를 쓴다.
     */
    public static final CubeDeformation OUTER = new CubeDeformation(1.0F);

    public MedievalArmorModel(ModelPart root) {
        super(root);
    }

    /** 투구: 머리 큐브 + 돔 + 바이저 + 테두리. */
    public static LayerDefinition createHelmetLayer() {
        MeshDefinition mesh = HumanoidModel.createMesh(OUTER, 0.0F);
        PartDefinition head = mesh.getRoot().getChild("head");

        // 정수리 돔. 머리보다 좁고 위로 얹혀 윤곽이 좁아진다.
        head.addOrReplaceChild(
                "medievalarms_crown",
                CubeListBuilder.create().texOffs(32, 0)
                        .addBox(-3.0F, -3.0F, -3.0F, 6.0F, 3.0F, 6.0F, new CubeDeformation(0.4F)),
                PartPose.offset(0.0F, -8.0F, 0.0F));

        // 얼굴 앞 바이저. 앞으로 튀어나와 평평한 앞면이 깨진다.
        head.addOrReplaceChild(
                "medievalarms_visor",
                CubeListBuilder.create().texOffs(32, 10)
                        .addBox(-4.0F, -1.0F, -1.0F, 8.0F, 2.0F, 1.0F, new CubeDeformation(0.2F)),
                PartPose.offset(0.0F, -4.0F, -5.0F));

        return LayerDefinition.create(mesh, 64, 32);
    }

    /** 흉갑: 몸통·팔 큐브 + 양어깨 견갑. */
    public static LayerDefinition createChestplateLayer() {
        MeshDefinition mesh = HumanoidModel.createMesh(OUTER, 0.0F);

        // 견갑은 팔에 붙인다. 팔을 따라 움직여야 자연스럽다.
        // 텍스처는 투구의 돔 칸을 같이 쓴다. 레이어가 같아 자리가 겹치지 않는다.
        mesh.getRoot().getChild("right_arm").addOrReplaceChild(
                "medievalarms_pauldron",
                CubeListBuilder.create().texOffs(32, 0)
                        .addBox(-4.0F, -3.0F, -3.0F, 6.0F, 3.0F, 6.0F, new CubeDeformation(0.5F)),
                PartPose.offset(0.0F, 0.0F, 0.0F));

        mesh.getRoot().getChild("left_arm").addOrReplaceChild(
                "medievalarms_pauldron",
                CubeListBuilder.create().texOffs(32, 0).mirror()
                        .addBox(-2.0F, -3.0F, -3.0F, 6.0F, 3.0F, 6.0F, new CubeDeformation(0.5F)),
                PartPose.offset(0.0F, 0.0F, 0.0F));

        return LayerDefinition.create(mesh, 64, 32);
    }
}
