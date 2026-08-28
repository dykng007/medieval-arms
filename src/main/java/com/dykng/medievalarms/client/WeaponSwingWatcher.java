package com.dykng.medievalarms.client;

import com.dykng.medievalarms.MedievalArms;
import com.dykng.medievalarms.weapon.MedievalWeaponItem;

import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.world.item.ItemStack;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.ClientTickEvent;

import java.util.Map;
import java.util.WeakHashMap;

/**
 * 누군가 이 모드의 무기를 휘두르기 시작하는 순간을 잡아내 애니메이션을 재생시킨다.
 *
 * <p><b>왜 매 틱 살펴보는가:</b> 애니메이션은 나 자신뿐 아니라 다른 플레이어에게도
 * 나와야 한다. 공격을 감지하는 이벤트는 대개 내 클라이언트의 내 공격만 알려주므로,
 * 다른 사람 것까지 챙기려면 모드가 직접 통신을 해야 한다.
 *
 * <p>그런데 바닐라는 누가 팔을 휘둘렀다는 사실을 이미 모두에게 보내준다
 * ({@code swinging}, {@code swingTime}). 그래서 그 값이 바뀌는 순간만 지켜보면
 * 통신 코드를 한 줄도 쓰지 않고 모든 플레이어의 동작을 처리할 수 있다.
 *
 * <p><b>휘두르기 시작을 판정하는 법:</b> 단순히 {@code swinging} 이 켜지는 순간만
 * 보면 연속 공격을 놓친다. 바닐라는 다음 공격을 시작할 때 {@code swinging} 을 끄지 않고
 * {@code swingTime} 만 처음으로 되돌리기 때문이다. 그래서 시간이 뒤로 감기는 것도
 * 새 공격으로 본다.
 */
@EventBusSubscriber(modid = MedievalArms.MOD_ID, value = Dist.CLIENT)
public final class WeaponSwingWatcher {

    private WeaponSwingWatcher() {
    }

    /**
     * 플레이어마다 지난 틱의 휘두르기 상태.
     *
     * <p>약한 참조 맵이라 플레이어가 시야에서 사라지면 항목도 알아서 없어진다.
     * 보통의 맵을 쓰면 서버를 옮겨 다닐수록 남은 항목이 계속 쌓인다.
     */
    private static final Map<AbstractClientPlayer, SwingState> SEEN = new WeakHashMap<>();

    /** 지난 틱에 본 값. */
    private static final class SwingState {
        boolean swinging;
        int swingTime;
    }

    @SubscribeEvent
    public static void onClientTick(ClientTickEvent.Post event) {
        ClientLevel level = Minecraft.getInstance().level;
        if (level == null) {
            SEEN.clear();       // 월드를 나갔다. 남은 상태는 의미가 없다.
            return;
        }

        for (AbstractClientPlayer player : level.players()) {
            SwingState previous = SEEN.computeIfAbsent(player, ignored -> new SwingState());

            boolean started = player.swinging
                    && (!previous.swinging || player.swingTime < previous.swingTime);

            previous.swinging = player.swinging;
            previous.swingTime = player.swingTime;

            if (started) {
                playFor(player);
            }
        }
    }

    /** 휘두르는 손에 이 모드 무기가 있으면 그 무기의 애니메이션을 재생한다. */
    private static void playFor(AbstractClientPlayer player) {
        ItemStack stack = player.getItemInHand(player.swingingArm);
        if (stack.getItem() instanceof MedievalWeaponItem weapon) {
            WeaponAnimations.play(player, weapon.getWeaponType().motion);
        }
    }
}
