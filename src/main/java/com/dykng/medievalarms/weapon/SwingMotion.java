package com.dykng.medievalarms.weapon;

/**
 * ★ 휘두르는 동작의 모양을 정하는 표.
 *
 * <p>여기 적힌 숫자가 실제 모션의 크기를 결정한다. 렌더링 코드를 건드리지 않고
 * 이 값만 바꿔도 동작이 달라지므로, 감이 안 맞으면 여기 숫자부터 조정하면 된다.
 * 값을 읽어 화면에 반영하는 곳은 {@code client.FirstPersonSwingRenderer} 이다.
 *
 * <p>비교 기준으로, 바닐라 검의 동작은 대략 pitch 80 / yaw 0 / 이동 없음에 해당한다.
 *
 * <p>각도는 도(degree), 이동은 마인크래프트 블록 단위(1.0 = 한 블록)다.
 */
public enum SwingMotion {

    //      아래로  옆으로  앞으로  내려감  속도감
    /** 베기 — 바닐라 검과 비슷하되 조금 더 빠르고 넓게. 장검용. */
    SLASH(70.0F, 15.0F, 0.05F, 0.10F, 1.10F),

    /** 찌르기 — 회전은 거의 없고 앞으로 쭉 뻗었다 당긴다. 창용. */
    THRUST(15.0F, 5.0F, 0.55F, 0.02F, 1.25F),

    /** 내리치기 — 위에서 아래로 크고 묵직하게. 철퇴·워해머용. */
    OVERHEAD(95.0F, 5.0F, 0.10F, 0.30F, 0.80F),

    /** 대각선 내려찍기 — 내리치기와 베기의 중간. 전투도끼용. */
    CHOP(80.0F, 30.0F, 0.10F, 0.22F, 0.90F),

    /** 넓게 후리기 — 좌에서 우로 크게 호를 그린다. 미늘창용. */
    SWEEP(30.0F, 70.0F, 0.05F, 0.10F, 0.95F);

    /** 위아래 회전(X축)의 최대 각도. 클수록 크게 내리친다. */
    public final float pitchDegrees;

    /** 좌우 회전(Y축)의 최대 각도. 클수록 옆으로 넓게 후린다. */
    public final float yawDegrees;

    /** 앞으로 내미는 거리. 찌르기 계열에서 크다. */
    public final float thrustDistance;

    /** 아래로 내려가는 거리. 내리치기 계열에서 크다. */
    public final float dropDistance;

    /**
     * 동작의 완급.
     *
     * <p>1.0이 기본이다. 1보다 크면 앞부분이 빨라 가볍고 날렵하게 느껴지고,
     * 1보다 작으면 앞부분이 느려 묵직하게 끌리는 느낌이 난다.
     *
     * <p>진행도에 {@code 1/speedScale} 제곱을 취하는 방식이라, 값을 어떻게 주든
     * 동작은 항상 처음부터 끝까지 온전히 재생된다. 중간에 잘리지 않는다.
     *
     * <p>실제 공격 쿨다운과는 무관한 순수 연출 값이다.
     * 공격 속도를 바꾸려면 {@link WeaponType}의 {@code attackSpeed}를 고쳐야 한다.
     */
    public final float speedScale;

    SwingMotion(float pitchDegrees, float yawDegrees, float thrustDistance, float dropDistance, float speedScale) {
        this.pitchDegrees = pitchDegrees;
        this.yawDegrees = yawDegrees;
        this.thrustDistance = thrustDistance;
        this.dropDistance = dropDistance;
        this.speedScale = speedScale;
    }
}
