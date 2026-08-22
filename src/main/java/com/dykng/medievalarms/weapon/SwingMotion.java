package com.dykng.medievalarms.weapon;

/**
 * ★ 휘두르는 동작의 궤적을 정하는 표.
 *
 * <p><b>구조가 왜 이렇게 생겼는지:</b> 처음에는 바닐라의 궤적 하나에 각도만 조금씩
 * 다르게 얹었다. 그랬더니 실제로 게임에서 보면 여섯 무기가 전부 똑같아 보였다.
 * 지배적인 움직임이 모든 무기에서 같았고, 10~20도짜리 차이는 그 안에 묻혀버렸기 때문이다.
 *
 * <p>그래서 동작을 <b>준비(windup)</b>와 <b>타격(strike)</b> 두 단계로 나눴다.
 * 무기마다 "어느 단계에서 어느 축으로 크게 움직이는가"가 달라지므로 궤적 자체가 갈린다.
 * 창은 뒤로 당겼다가 앞으로 내지르고, 철퇴는 위로 들었다가 아래로 내리찍고,
 * 미늘창은 옆으로 크게 후린다. 숫자가 아니라 방향이 다르다.
 *
 * <p><b>두 단계가 모두 0으로 끝나야 하는 이유:</b> 마인크래프트의 스윙 진행도는
 * 0에서 1까지 올라간 뒤 곧바로 0으로 되돌아간다. 진행도 1에서의 자세가 평상시 자세와
 * 다르면 그 순간 무기가 툭 끊겨 보인다. 그래서 두 단계 곡선 모두 시작과 끝에서 0이 된다.
 *
 * <p>각도는 도(degree), 이동은 마인크래프트 블록 단위(1.0 = 한 블록)다.
 * 여기 적는 값이 그 단계에서의 <i>최대치</i>가 되도록 정규화되어 있으므로,
 * "타격 때 120도 내리친다"는 뜻으로 그대로 읽으면 된다.
 */
public enum SwingMotion {

    //        준비:위로  타격:아래로  준비:뒤로  타격:앞으로  타격:옆으로  완급
    /** 베기 — 적당히 들었다가 비스듬히 그어내린다. 장검용. */
    SLASH(25.0F, 75.0F, 0.05F, 0.12F, 25.0F, 1.05F),

    /** 찌르기 — 회전은 거의 없이 뒤로 당겼다가 앞으로 내지른다. 창용. */
    THRUST(10.0F, 18.0F, 0.30F, 0.55F, 0.0F, 1.20F),

    /** 내리치기 — 크게 치켜들었다가 아래로 내리찍는다. 철퇴·워해머용. */
    OVERHEAD(70.0F, 120.0F, 0.10F, 0.15F, 5.0F, 0.85F),

    /** 대각선 내려찍기 — 내리치기에 옆으로 도는 힘이 섞인다. 전투도끼용. */
    CHOP(50.0F, 92.0F, 0.08F, 0.14F, 60.0F, 0.92F),

    /** 넓게 후리기 — 위아래보다 좌우로 크게 호를 그린다. 미늘창용. */
    SWEEP(15.0F, 30.0F, 0.05F, 0.10F, 90.0F, 1.00F);

    /** 준비 단계에서 무기를 위로 치켜드는 각도. 클수록 크게 반동을 준다. */
    public final float windupPitch;

    /** 타격 단계에서 아래로 내리치는 각도. 이 모션의 성격을 가장 크게 좌우한다. */
    public final float strikePitch;

    /** 준비 단계에서 몸쪽으로 당기는 거리. 찌르기에서 크다. */
    public final float windupPull;

    /** 타격 단계에서 앞으로 내미는 거리. 찌르기에서 크다. */
    public final float strikeReach;

    /** 타격 단계에서 옆으로 후리는 각도. 후리기에서 크다. */
    public final float strikeYaw;

    /**
     * 동작의 완급.
     *
     * <p>1.0이 기본이다. 1보다 크면 앞부분이 빨라 가볍고 날렵하게 느껴지고,
     * 1보다 작으면 앞부분이 느려 묵직하게 끌리는 느낌이 난다.
     * 진행도에 {@code 1/speedScale} 제곱을 취하는 방식이라, 값을 어떻게 주든
     * 동작은 처음부터 끝까지 온전히 재생된다.
     *
     * <p>실제 공격 쿨다운과는 무관한 순수 연출 값이다.
     * 공격 속도를 바꾸려면 {@link WeaponType}의 {@code attackSpeed}를 고쳐야 한다.
     */
    public final float speedScale;

    SwingMotion(float windupPitch, float strikePitch,
                float windupPull, float strikeReach,
                float strikeYaw, float speedScale) {
        this.windupPitch = windupPitch;
        this.strikePitch = strikePitch;
        this.windupPull = windupPull;
        this.strikeReach = strikeReach;
        this.strikeYaw = strikeYaw;
        this.speedScale = speedScale;
    }
}
