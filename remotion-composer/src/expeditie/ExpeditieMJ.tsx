import React from "react";
import {
  AbsoluteFill, Audio, Img, OffthreadVideo, Sequence, staticFile,
  interpolate, spring, useCurrentFrame, useVideoConfig,
} from "remotion";

export type ShotSpec = { id: string; frames: number };
export type ExpeditieProps = {
  shots: ShotSpec[];
  music?: string | null;
  musicVolume: number;
  /** map onder public/ waar de shots staan, zodat een fixronde naast het origineel kan bestaan */
  clipDir?: string;
  /**
   * Muziek per shot in plaats van een constant niveau: warm in de titel en op het
   * beloningsmoment, vrijwel weg in de scenes waar de geluidseffecten het werk doen.
   * Lijst van [frame, volume]-punten, oplopend in frame. Leeg = terug naar musicVolume.
   */
  musicEnvelope?: [number, number][];
  /** frame-vensters voor de grafische laag, berekend uit de montage */
  titleWindow: [number, number];
  errorWindow: [number, number];
  rewardWindow: [number, number];
  fadeStart: number;
  /** extra frames achter het laatste shot voor de eindkaart (punt 9) */
  outroFrames?: number;
  /** frame waarop het logo begint op te komen; standaard net voor het beeld zwart is */
  endCardStart?: number;
};

const MJ_YELLOW = "#F5C518";
const MJ_BROWN = "#4A2C17";
const MJ_TEAL = "#2FB8A8";

/** Titel: het echte logo veert in en houdt vast tot de duik het bladerdak in. */
const TitleLogo: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = spring({ frame, fps, config: { damping: 12, mass: 0.7 } });
  const out = interpolate(frame, [fps * 3.2, fps * 4.2], [1, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill style={{ justifyContent: "flex-start", alignItems: "center", paddingTop: 54 }}>
      <Img
        src={staticFile("expeditie-mj/mj-logo.png")}
        style={{
          width: 620, opacity: out,
          transform: `scale(${0.72 + pop * 0.28}) translateY(${(1 - pop) * -40}px)`,
          filter: "drop-shadow(0 10px 26px rgba(0,0,0,.45))",
        }}
      />
    </AbsoluteFill>
  );
};

/** Foutmelding over het vastgelopen scherm: doorgestreept wifi-icoon plus tekst. */
const NoConnection: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const inA = interpolate(frame, [0, fps * 0.35], [0, 1], { extrapolateRight: "clamp" });
  const flicker = frame % 14 < 2 ? 0.55 : 1;
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
      <div style={{ opacity: inA * flicker, textAlign: "center", transform: "translateY(6px)" }}>
        <svg width="120" height="120" viewBox="0 0 24 24" style={{ marginBottom: 6 }}>
          <g fill="none" stroke="#FFFFFF" strokeWidth="1.7" strokeLinecap="round">
            <path d="M2.5 8.5a15 15 0 0 1 19 0" opacity=".9" />
            <path d="M5.5 12a11 11 0 0 1 13 0" opacity=".7" />
            <path d="M8.5 15.5a7 7 0 0 1 7 0" opacity=".55" />
            <circle cx="12" cy="19" r="1.15" fill="#FFFFFF" stroke="none" />
            <path d="M3.5 3.5l17 17" stroke="#FF4B3E" strokeWidth="2.1" />
          </g>
        </svg>
        <div style={{
          fontFamily: "system-ui, -apple-system, Helvetica, sans-serif",
          fontSize: 42, fontWeight: 800, letterSpacing: -0.5, color: "#FFFFFF",
          textShadow: "0 3px 14px rgba(0,0,0,.7)",
        }}>Geen verbinding meer</div>
      </div>
    </AbsoluteFill>
  );
};

/** Beloningsmoment: gouden stralenkrans plus label, game-achtig zoals afgesproken. */
const RewardBurst: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const pop = spring({ frame, fps, config: { damping: 10, mass: 0.6 } });
  const spin = frame * 0.55;
  const label = spring({ frame: frame - fps * 0.45, fps, config: { damping: 13 } });
  const rays = Array.from({ length: 22 });
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <svg width={width} height={height} style={{ opacity: 0.55 * pop }}>
          <g transform={`translate(${width / 2} ${height / 2}) rotate(${spin})`}>
            {rays.map((_, i) => (
              <polygon key={i}
                transform={`rotate(${(360 / rays.length) * i})`}
                points={`0,-26 0,26 ${420 * pop},8 ${420 * pop},-8`}
                fill={i % 2 ? "#FFE082" : MJ_YELLOW} opacity={i % 2 ? 0.42 : 0.62} />
            ))}
          </g>
        </svg>
      </AbsoluteFill>
      <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: 62 }}>
        <div style={{
          transform: `scale(${0.8 + label * 0.2})`, opacity: label,
          background: MJ_BROWN, border: `5px solid ${MJ_YELLOW}`, borderRadius: 20,
          padding: "16px 40px", boxShadow: "0 14px 34px rgba(0,0,0,.5)",
          fontFamily: "system-ui, -apple-system, Helvetica, sans-serif", textAlign: "center",
        }}>
          <div style={{ fontSize: 21, fontWeight: 800, letterSpacing: 3.6, color: MJ_TEAL }}>BELONING</div>
          <div style={{ fontSize: 54, fontWeight: 900, letterSpacing: -1, color: MJ_YELLOW, lineHeight: 1.02 }}>De Jeep</div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/** Eindkaart: het logo komt op terwijl het beeld zwart wordt, houdt vast, en fadet weg.
 *  Geeft de film een punt in plaats van een afkapping (punt 9). */
const EndCard: React.FC<{ frames: number }> = ({ frames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = spring({ frame, fps, config: { damping: 14, mass: 0.8 } });
  const out = interpolate(frame, [frames - fps * 0.5, frames - 1], [1, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
      <Img
        src={staticFile("expeditie-mj/mj-logo.png")}
        style={{
          width: 560, opacity: pop * out,
          transform: `scale(${0.82 + pop * 0.18})`,
          filter: "drop-shadow(0 10px 26px rgba(0,0,0,.55))",
        }}
      />
    </AbsoluteFill>
  );
};

export const ExpeditieMJ: React.FC<ExpeditieProps> = ({
  shots, music, musicVolume, musicEnvelope, clipDir, titleWindow, errorWindow, rewardWindow,
  fadeStart, outroFrames, endCardStart,
}) => {
  const dir = clipDir ?? "expeditie-mj";
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  // interpolate eist een strikt oplopende invoerreeks; dubbele frames eruit filteren.
  const env = (musicEnvelope ?? []).filter(
    (p, i, all) => i === 0 || p[0] > all[i - 1][0],
  );
  let cursor = 0;
  const placed = shots.map((s) => { const from = cursor; cursor += s.frames; return { ...s, from }; });
  const outro = outroFrames ?? 0;
  const shotsEnd = cursor;
  const cardFrom = endCardStart ?? Math.max(0, shotsEnd - 12);
  const fade = interpolate(frame, [fadeStart, shotsEnd - 1], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill style={{ backgroundColor: "#000000" }}>
      {placed.map((s) => (
        <Sequence key={s.id} from={s.from} durationInFrames={s.frames}>
          <OffthreadVideo src={staticFile(`${dir}/${s.id}.mp4`)} style={{ width: "100%", height: "100%" }} />
        </Sequence>
      ))}

      {music ? (
        <Audio src={staticFile(`expeditie-mj/${music}`)} volume={(f) =>
          env.length >= 2
            ? interpolate(f, env.map((p) => p[0]), env.map((p) => p[1]),
                { extrapolateLeft: "clamp", extrapolateRight: "clamp" })
            : interpolate(f, [0, fps * 1.2, durationInFrames - fps * 1.6, durationInFrames],
                [0, musicVolume, musicVolume, 0],
                { extrapolateLeft: "clamp", extrapolateRight: "clamp" })} />
      ) : null}

      <Sequence from={titleWindow[0]} durationInFrames={titleWindow[1] - titleWindow[0]}><TitleLogo /></Sequence>
      <Sequence from={errorWindow[0]} durationInFrames={errorWindow[1] - errorWindow[0]}><NoConnection /></Sequence>
      <Sequence from={rewardWindow[0]} durationInFrames={rewardWindow[1] - rewardWindow[0]}><RewardBurst /></Sequence>

      <AbsoluteFill style={{ backgroundColor: "#000000", opacity: fade, pointerEvents: "none" }} />

      {outro > 0 ? (
        <Sequence from={cardFrom} durationInFrames={durationInFrames - cardFrom}>
          <EndCard frames={durationInFrames - cardFrom} />
        </Sequence>
      ) : null}
    </AbsoluteFill>
  );
};
