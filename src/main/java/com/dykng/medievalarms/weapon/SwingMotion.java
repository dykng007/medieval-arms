package com.dykng.medievalarms.weapon;

/**
 * 무기를 휘두를 때의 동작 종류.
 *
 * <p>여기 담긴 숫자들이 실제 모션의 크기를 결정한다. 값만 바꿔도 모션이 달라지므로,
 * 렌더링 코드를 건드리지 않고 감을 조정할 수 있다. 실제로 이 값을 읽어 화면에 반영하는 곳은
 * {@code client.FirstPersonSwingRenderer} 이다.
 *
 * <p>각도는 도(degree) 단위, 이동은 마인크래프트 블록 단위(1.0 = 한 블록)다.
 */
public enum SwingMotion {

    /** 베기 — 바닐라 검과 비슷하되 조금 더 빠르고 얕게. */
    SLASH(35.0F, 12.0F, 0.00F, 0.35F, 1.0F),

    /** 찌르기 — 회전은 거의 없고 앞으로 쭉 뻗었다 당긴다. 창 계열. */
    THRUST(8.0F, 3.0F, 0.65F, 0.05F, 1.25F),

    /** 내리치기 — 위에서 아래로 크게. 철퇴·워해머 계열. 묵직하게 느리다. */
    OVERHEAD(75.0F, 6.0F, 0.15F, 0.55F, 0.8F),

    /** 대각선 내려찍기 — 도끼 계열. 내리치기와 베기의 중간. */
    CHOP(58.0F, 26.0F, 0.10F, 0.45F, 0.9F),

    /** 넓게 후리기 — 좌에서 우로 크게 호를 그린다. 미늘창 계열. */
    SWEEP(20.0F, 60.0F, 0.05F, 0.20F, 0.95F);

    /** 위아래 회전(X축)의 최대 각도. 클수록 크게 내리친다. */
    public final float pitchDegrees;
    /** 좌우 회전(Y축)의 최대 각도. 클수록 옆으로 넓게 휘두른다. */
    public final float yawDegrees;
    /** 앞으로 내미는 거리. 찌르기 계열에서 크다. */
    public final float thrustDistance;
    /** 아래로 내려가는 거리. 내리치기 계열에서 크다. */
    public final float dropDistance;
    /**
     * 모션 진행 속도 배수. 1.0이 기본이고, 작을수록 묵직하게 늘어진다.
     * 실제 공격 쿨다운과는 무관한 순수 연출 값이다.
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
