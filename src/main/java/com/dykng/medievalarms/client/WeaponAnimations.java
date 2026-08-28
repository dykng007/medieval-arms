package com.dykng.medievalarms.client;

import com.dykng.medievalarms.MedievalArms;
import com.dykng.medievalarms.weapon.SwingMotion;

import dev.kosmx.playerAnim.api.firstPerson.FirstPersonConfiguration;
import dev.kosmx.playerAnim.api.firstPerson.FirstPersonMode;
import dev.kosmx.playerAnim.api.layered.IAnimation;
import dev.kosmx.playerAnim.api.layered.KeyframeAnimationPlayer;
import dev.kosmx.playerAnim.api.layered.ModifierLayer;
import dev.kosmx.playerAnim.api.layered.modifier.AbstractFadeModifier;
import dev.kosmx.playerAnim.core.data.KeyframeAnimation;
import dev.kosmx.playerAnim.core.util.Ease;
import dev.kosmx.playerAnim.minecraftApi.PlayerAnimationAccess;
import dev.kosmx.playerAnim.minecraftApi.PlayerAnimationFactory;
import dev.kosmx.playerAnim.minecraftApi.PlayerAnimationRegistry;

import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.api.distmarker.OnlyIn;

import java.util.EnumMap;
import java.util.Locale;
import java.util.Map;

/**
 * 무기를 휘두를 때 플레이어에게 애니메이션을 재생한다.
 *
 * <p><b>왜 라이브러리를 쓰는가:</b> 예전에는 손에 든 아이템 하나만 회전·이동시켰다.
 * 팔도 몸도 그대로라 무기만 허공에서 떠다니는 것처럼 보였고, 숫자를 아무리 맞춰도
 * 그 한계는 넘지 못했다. 사람이 창을 지를 때 실제로 움직이는 것은 무기가 아니라 몸이다.
 * PlayerAnimator 는 팔·몸통·머리를 한꺼번에 움직이는 진짜 애니메이션을 재생해준다.
 *
 * <p><b>동작 방식:</b> 라이브러리는 플레이어마다 애니메이션 "층"을 하나씩 갖게 해준다.
 * 우리는 {@link #LAYER_ID} 라는 이름으로 빈 층을 하나 등록해두고, 무기를 휘두르는 순간
 * 그 층에 해당 무기의 애니메이션을 밀어 넣는다. 층을 쓰기 때문에 다른 모드가 같은
 * 플레이어에게 애니메이션을 재생해도 서로 덮어쓰지 않는다.
 *
 * <p><b>애니메이션 파일:</b> {@code assets/medievalarms/player_animations/*.json}.
 * 폴더 이름의 끝 s 를 빠뜨리면 라이브러리가 경고만 남기고 넘어가므로 주의한다.
 * 내용은 {@code tools/gen_animations.py} 가 만든다. JSON 을 직접 고치지 말고
 * 그 스크립트의 각도를 고친 뒤 다시 실행하는 편이 낫다.
 */
@OnlyIn(Dist.CLIENT)
public final class WeaponAnimations {

    private WeaponAnimations() {
    }

    /**
     * 이 모드가 쓰는 애니메이션 층의 이름.
     * 재생할 때 같은 이름으로 다시 찾아야 하므로 한곳에 두었다.
     */
    public static final ResourceLocation LAYER_ID =
            ResourceLocation.fromNamespaceAndPath(MedievalArms.MOD_ID, "weapon_swing");

    /**
     * 층을 등록할 때 쓰는 우선순위. 값이 클수록 나중에(위에) 얹힌다.
     * 다른 모드와 겹칠 일이 거의 없는 평범한 값을 골랐다.
     */
    private static final int LAYER_PRIORITY = 1000;

    /** 이전 동작에서 새 동작으로 넘어갈 때 섞이는 시간(틱). 짧아야 공격이 굼떠 보이지 않는다. */
    private static final int FADE_TICKS = 2;

    /** 모션 종류 -> 애니메이션 파일 위치. 매번 문자열을 만들지 않도록 미리 계산해둔다. */
    private static final Map<SwingMotion, ResourceLocation> FILES = new EnumMap<>(SwingMotion.class);

    static {
        for (SwingMotion motion : SwingMotion.values()) {
            // THRUST -> medievalarms:thrust -> player_animations/thrust.json
            FILES.put(motion, ResourceLocation.fromNamespaceAndPath(
                    MedievalArms.MOD_ID, motion.name().toLowerCase(Locale.ROOT)));
        }
    }

    /**
     * 플레이어마다 빈 애니메이션 층을 하나씩 만들어 붙인다.
     * 클라이언트 설정 단계에서 한 번만 부르면 된다.
     */
    public static void register() {
        PlayerAnimationFactory.ANIMATION_DATA_FACTORY.registerFactory(
                LAYER_ID, LAYER_PRIORITY, player -> new ModifierLayer<>());
    }

    /**
     * 한 플레이어에게 무기 모션에 맞는 애니메이션을 재생한다.
     *
     * <p>반드시 클라이언트에서만 불러야 한다. 서버에는 이 클래스도 라이브러리도 없다.
     * 다른 플레이어의 동작도 여기서 재생한다. 휘두르는 상태는 바닐라가 이미
     * 모두에게 알려주므로 이 모드가 따로 통신할 필요가 없다.
     */
    public static void play(AbstractClientPlayer player, SwingMotion motion) {
        ModifierLayer<IAnimation> layer = layerOf(player);
        if (layer == null) {
            return;     // 라이브러리가 아직 이 플레이어를 모르는 경우. 다음 공격에 다시 시도된다.
        }

        // 리소스팩이 애니메이션을 빼버렸을 수도 있으므로 없으면 조용히 넘어간다.
        // 여기서 터지면 렌더 스레드가 통째로 죽는다.
        if (!(PlayerAnimationRegistry.getAnimation(FILES.get(motion)) instanceof KeyframeAnimation animation)) {
            return;
        }

        KeyframeAnimationPlayer play = new KeyframeAnimationPlayer(animation)
                // 1인칭에서도 같은 애니메이션을 보여준다. 이렇게 하지 않으면 3인칭만
                // 애니메이션이 나오고 정작 본인 화면에서는 바닐라 동작이 나온다.
                .setFirstPersonMode(FirstPersonMode.THIRD_PERSON_MODEL)
                // 1인칭 화면에 무엇을 보여줄지. 창이나 미늘창은 두 손으로 잡으므로
                // 양팔을 다 보여줘야 한 손이 허공에 뜬 것처럼 보이지 않는다.
                .setFirstPersonConfiguration(new FirstPersonConfiguration()
                        .setShowRightArm(true)
                        .setShowLeftArm(true)
                        .setShowRightItem(true)
                        .setShowLeftItem(true));

        // 갑자기 자세가 튀지 않도록 짧게 섞으면서 바꾼다.
        layer.replaceAnimationWithFade(
                AbstractFadeModifier.standardFadeIn(FADE_TICKS, Ease.INOUTSINE), play);
    }

    /** 이 플레이어에게 붙여둔 우리 층을 찾는다. 없으면 {@code null}. */
    @SuppressWarnings("unchecked")     // 층을 만든 것도 우리라 실제 형은 항상 맞다
    private static ModifierLayer<IAnimation> layerOf(AbstractClientPlayer player) {
        IAnimation found = PlayerAnimationAccess.getPlayerAssociatedData(player).get(LAYER_ID);
        return found instanceof ModifierLayer ? (ModifierLayer<IAnimation>) found : null;
    }
}
