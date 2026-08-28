package com.dykng.medievalarms.weapon;

/**
 * 무기를 휘두르는 동작의 종류.
 *
 * <p>여기에는 숫자가 없다. 이 열거형은 "어떤 종류의 동작인가"만 정하고,
 * 실제 움직임은 애니메이션 파일에 들어 있다.
 *
 * <p><b>동작을 고치려면:</b> {@code tools/gen_animations.py} 의 각도를 고치고
 * 다시 실행한다. 이름이 같은 JSON 이
 * {@code assets/medievalarms/player_animations/} 에 다시 만들어진다.
 * 예를 들어 {@link #THRUST} 는 {@code thrust.json} 을 쓴다.
 *
 * <p><b>왜 숫자를 들고 있지 않은가:</b> 예전에는 이 열거형이 각도와 거리 여섯 개를
 * 들고 있었고, 그 값으로 손에 든 아이템을 회전·이동시켰다. 팔도 몸도 움직이지 않아
 * 무기만 허공에서 떠다니는 것처럼 보였고, 숫자를 아무리 맞춰도 그 한계는 넘지 못했다.
 * 지금은 팔·몸통·머리가 함께 움직이는 키프레임 애니메이션을 쓴다.
 *
 * <p>새 동작을 추가하려면 여기에 상수를 하나 넣고, 같은 이름(소문자)의 JSON 을
 * 만들고, {@link com.dykng.medievalarms.client.ModArmPoses#forMotion} 에
 * 들고 있을 때의 자세를 정해주면 된다.
 */
public enum SwingMotion {

    /** 베기 — 칼을 뒤로 뺐다가 대각선으로 그어내린다. 장검용. */
    SLASH,

    /** 찌르기 — 몸을 꼬았다가 풀면서 정면으로 내지른다. 창용. */
    THRUST,

    /** 내리치기 — 머리 위로 넘겼다가 몸을 접으며 내리찍는다. 철퇴·워해머용. */
    OVERHEAD,

    /** 대각선 내려찍기 — 내리치기에 몸통 회전이 섞인다. 전투도끼용. */
    CHOP,

    /** 넓게 후리기 — 위아래보다 좌우로 크게 호를 그린다. 미늘창용. */
    SWEEP
}
