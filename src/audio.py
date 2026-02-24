"""
GRIT - Audio System v2
Generates synth music and sound effects procedurally using numpy.
Features: detuned oscillators, LFO modulation, filter sweeps, arpeggios,
          PWM, layered drums, reverb-like delay.
"""

import io
import wave
import numpy as np

SAMPLE_RATE = 44100

# ─── Note frequencies ──────────────────────────────────────
NOTE_FREQ = {}
for _oct in range(1, 7):
    for _i, _name in enumerate(['C', 'Cs', 'D', 'Ds', 'E', 'F',
                                 'Fs', 'G', 'Gs', 'A', 'As', 'B']):
        NOTE_FREQ[f'{_name}{_oct}'] = 32.7032 * (2 ** (_oct - 1)) * (2 ** (_i / 12))
NOTE_FREQ['R'] = 0


# ─── Core Waveform Generators ─────────────────────────────
def _t(dur):
    """Time array."""
    return np.linspace(0, dur, int(SAMPLE_RATE * dur), endpoint=False, dtype=np.float32)


def _saw(freq, dur, vol=0.25):
    """Sawtooth wave - rich harmonics, classic synth sound."""
    n = int(SAMPLE_RATE * dur)
    if freq == 0 or n == 0:
        return np.zeros(n, dtype=np.float32)
    t = _t(dur)
    phase = (t * freq) % 1.0
    return ((2 * phase - 1) * vol).astype(np.float32)


def _square(freq, dur, vol=0.2):
    n = int(SAMPLE_RATE * dur)
    if freq == 0 or n == 0:
        return np.zeros(n, dtype=np.float32)
    t = _t(dur)
    return (np.sign(np.sin(2 * np.pi * freq * t)) * vol).astype(np.float32)


def _sine(freq, dur, vol=0.25):
    n = int(SAMPLE_RATE * dur)
    if freq == 0 or n == 0:
        return np.zeros(n, dtype=np.float32)
    t = _t(dur)
    return (np.sin(2 * np.pi * freq * t) * vol).astype(np.float32)


def _triangle(freq, dur, vol=0.28):
    n = int(SAMPLE_RATE * dur)
    if freq == 0 or n == 0:
        return np.zeros(n, dtype=np.float32)
    t = _t(dur)
    phase = (t * freq) % 1.0
    return ((2 * np.abs(2 * phase - 1) - 1) * vol).astype(np.float32)


def _noise(dur, vol=0.15):
    n = int(SAMPLE_RATE * dur)
    return (np.random.uniform(-1, 1, n) * vol).astype(np.float32)


def _pwm(freq, dur, lfo_rate=3.0, base_duty=0.5, lfo_depth=0.25, vol=0.2):
    """Pulse wave with LFO-modulated pulse width for animated synth timbre."""
    n = int(SAMPLE_RATE * dur)
    if freq == 0 or n == 0:
        return np.zeros(n, dtype=np.float32)
    t = _t(dur)
    duty = base_duty + lfo_depth * np.sin(2 * np.pi * lfo_rate * t)
    duty = np.clip(duty, 0.1, 0.9)
    phase = (t * freq) % 1.0
    return (np.where(phase < duty, vol, -vol)).astype(np.float32)


# ─── Synth Building Blocks ────────────────────────────────
def _detune(freq, dur, wave_fn=_saw, detune_cents=8, vol=0.2):
    """Two detuned oscillators mixed for fat analog synth sound."""
    ratio = 2 ** (detune_cents / 1200)
    a = wave_fn(freq * ratio, dur, vol * 0.55)
    b = wave_fn(freq / ratio, dur, vol * 0.55)
    return a + b


def _supersaw(freq, dur, vol=0.18, voices=3, spread=12):
    """Multiple detuned saws for huge lead/pad sound."""
    n = int(SAMPLE_RATE * dur)
    if freq == 0 or n == 0:
        return np.zeros(n, dtype=np.float32)
    out = np.zeros(n, dtype=np.float32)
    for i in range(voices):
        cents = spread * (i / (voices - 1) - 0.5) * 2 if voices > 1 else 0
        ratio = 2 ** (cents / 1200)
        out += _saw(freq * ratio, dur, vol / voices)
    return out


def _lp_filter(signal, cutoff_hz, resonance=0.3):
    """Simple one-pole low-pass filter for warmth."""
    rc = 1.0 / (2 * np.pi * max(cutoff_hz, 20))
    dt = 1.0 / SAMPLE_RATE
    alpha = dt / (rc + dt)
    out = np.zeros_like(signal)
    prev = 0.0
    fb = resonance * 0.9
    for i in range(len(signal)):
        inp = signal[i] - fb * prev
        prev = prev + alpha * (inp - prev)
        out[i] = prev
    return out.astype(np.float32)


def _lp_filter_sweep(signal, start_hz, end_hz, resonance=0.2):
    """Low-pass filter with sweeping cutoff for brightness control."""
    n = len(signal)
    out = np.zeros(n, dtype=np.float32)
    prev = 0.0
    fb = resonance * 0.85
    for i in range(n):
        ratio = i / max(n - 1, 1)
        cutoff = start_hz + (end_hz - start_hz) * ratio
        rc = 1.0 / (2 * np.pi * max(cutoff, 20))
        dt = 1.0 / SAMPLE_RATE
        alpha = dt / (rc + dt)
        inp = signal[i] - fb * prev
        prev = prev + alpha * (inp - prev)
        out[i] = prev
    return out.astype(np.float32)


def _adsr(signal, attack=0.02, decay=0.05, sustain=0.7, release=0.1):
    """ADSR envelope for expressive shaping."""
    n = len(signal)
    a = min(int(SAMPLE_RATE * attack), n // 4)
    d = min(int(SAMPLE_RATE * decay), n // 4)
    r = min(int(SAMPLE_RATE * release), n // 3)
    s_len = max(0, n - a - d - r)

    env = np.ones(n, dtype=np.float32)
    pos = 0
    if a > 0:
        env[pos:pos + a] = np.linspace(0, 1, a, dtype=np.float32)
        pos += a
    if d > 0:
        env[pos:pos + d] = np.linspace(1, sustain, d, dtype=np.float32)
        pos += d
    if s_len > 0:
        env[pos:pos + s_len] = sustain
        pos += s_len
    if r > 0:
        env[pos:pos + r] = np.linspace(sustain, 0, r, dtype=np.float32)

    return signal * env


def _delay(signal, delay_ms=120, feedback=0.3, wet=0.25):
    """Simple delay effect for space and depth."""
    delay_samples = int(SAMPLE_RATE * delay_ms / 1000)
    out = signal.copy()
    for i in range(delay_samples, len(out)):
        out[i] += out[i - delay_samples] * feedback
    return signal * (1 - wet) + out * wet


def _mix(*arrays):
    """Mix arrays of potentially different lengths."""
    if not arrays:
        return np.zeros(0, dtype=np.float32)
    max_len = max(len(a) for a in arrays)
    out = np.zeros(max_len, dtype=np.float32)
    for a in arrays:
        out[:len(a)] += a
    return out


def _place(signal, offset_samples, total_len):
    """Place a signal at a sample offset within a buffer."""
    out = np.zeros(total_len, dtype=np.float32)
    end = min(offset_samples + len(signal), total_len)
    seg_len = end - offset_samples
    if seg_len > 0 and offset_samples >= 0:
        out[offset_samples:end] = signal[:seg_len]
    return out


# ─── Synth Note Helper ────────────────────────────────────
def _synth_note(freq, dur, wave_type='supersaw', vol=0.18,
                filter_start=3000, filter_end=800):
    """Create a single synth note with filter sweep."""
    if freq == 0:
        return np.zeros(int(SAMPLE_RATE * dur), dtype=np.float32)

    if wave_type == 'supersaw':
        w = _supersaw(freq, dur, vol=vol)
    elif wave_type == 'detune':
        w = _detune(freq, dur, _saw, vol=vol)
    elif wave_type == 'pwm':
        w = _pwm(freq, dur, vol=vol)
    elif wave_type == 'square':
        w = _square(freq, dur, vol=vol)
    elif wave_type == 'triangle':
        w = _triangle(freq, dur, vol=vol)
    elif wave_type == 'sine':
        w = _sine(freq, dur, vol=vol)
    elif wave_type == 'saw':
        w = _saw(freq, dur, vol=vol)
    else:
        w = _saw(freq, dur, vol=vol)

    # Filter sweep
    if filter_start != filter_end:
        w = _lp_filter_sweep(w, filter_start, filter_end, resonance=0.15)
    elif filter_start < 10000:
        w = _lp_filter(w, filter_start, resonance=0.15)

    return w


def _seq(notes, beat_dur, wave_type='supersaw', vol=0.16,
         attack=0.01, decay=0.04, sustain=0.6, release=0.06,
         filter_start=4000, filter_end=1200):
    """Play a note sequence with synth voice and ADSR."""
    parts = []
    for note, beats in notes:
        freq = NOTE_FREQ.get(note, 0)
        dur = beats * beat_dur
        if freq > 0:
            w = _synth_note(freq, dur, wave_type, vol, filter_start, filter_end)
            w = _adsr(w, attack, decay, sustain, release)
        else:
            w = np.zeros(int(SAMPLE_RATE * dur), dtype=np.float32)
        parts.append(w)
    return np.concatenate(parts) if parts else np.zeros(0, dtype=np.float32)


# ─── Drum Synthesis ────────────────────────────────────────
def _drum_kick(dur=0.15):
    """Punchy synth kick: sine sweep + click transient."""
    n = int(SAMPLE_RATE * dur)
    t = _t(dur)[:n]
    freq = 160 * np.exp(-t * 20) + 40
    phase = np.cumsum(freq / SAMPLE_RATE)
    body = np.sin(2 * np.pi * phase) * 0.4
    click = _noise(0.008, vol=0.3)
    click = _adsr(click, attack=0.001, decay=0.005, sustain=0, release=0.002)
    out = body * np.exp(-t * 15).astype(np.float32)
    out[:len(click)] += click
    return out.astype(np.float32)


def _drum_snare(dur=0.12):
    """Snare: filtered noise + sine body."""
    n = int(SAMPLE_RATE * dur)
    t = _t(dur)[:n]
    noise = _noise(dur, vol=0.22)
    noise = _lp_filter(noise, 6000, resonance=0.1)
    body = _sine(180, dur, vol=0.15)
    out = noise + body[:n]
    out *= np.exp(-t * 18).astype(np.float32)
    return out.astype(np.float32)


def _drum_hihat(dur=0.05, open_hat=False):
    """Hi-hat: high-pass filtered noise."""
    actual_dur = dur * (3 if open_hat else 1)
    n = int(SAMPLE_RATE * actual_dur)
    t = _t(actual_dur)[:n]
    noise = _noise(actual_dur, vol=0.12)
    lp = _lp_filter(noise, 2000)
    hp = noise - lp
    decay = 25 if not open_hat else 8
    hp *= np.exp(-t * decay).astype(np.float32)
    return hp.astype(np.float32)


# ─── Arpeggiator ──────────────────────────────────────────
def _arpeggio(chord_freqs, dur, step_dur=0.08, wave_type='pwm', vol=0.12):
    """Arpeggiator cycling through chord tones."""
    n = int(SAMPLE_RATE * dur)
    out = np.zeros(n, dtype=np.float32)
    step_samples = int(SAMPLE_RATE * step_dur)
    idx = 0
    pos = 0
    while pos < n:
        freq = chord_freqs[idx % len(chord_freqs)]
        note_len = min(step_samples, n - pos)
        note_dur = note_len / SAMPLE_RATE
        w = _synth_note(freq, note_dur, wave_type, vol, 3000, 1500)
        w = _adsr(w, attack=0.005, decay=0.02, sustain=0.4, release=0.03)
        out[pos:pos + len(w)] += w
        pos += step_samples
        idx += 1
    return out


# ─── Music: Menu Theme ─────────────────────────────────────
def _generate_menu_music():
    """Atmospheric synth — Am/Em progression, pads and arpeggios."""
    bpm = 78
    beat = 60.0 / bpm
    total_beats = 32
    total_dur = total_beats * beat
    total_samples = int(SAMPLE_RATE * total_dur)

    # ── Pad (long sustained chords with supersaw) ──
    pad_chords = [
        (['A2', 'E3', 'A3', 'C4'], 8),
        (['F2', 'C3', 'F3', 'A3'], 8),
        (['G2', 'D3', 'G3', 'B3'], 8),
        (['E2', 'B2', 'E3', 'G3'], 8),
    ]
    pad = np.zeros(total_samples, dtype=np.float32)
    pos = 0
    for notes, beats in pad_chords:
        dur = beats * beat
        chord_len = int(SAMPLE_RATE * dur)
        chord = np.zeros(chord_len, dtype=np.float32)
        for note in notes:
            freq = NOTE_FREQ.get(note, 0)
            if freq > 0:
                w = _supersaw(freq, dur, vol=0.04, voices=3, spread=10)
                w = _lp_filter(w, 1200, resonance=0.05)
                w = _adsr(w, attack=0.8, decay=0.3, sustain=0.7, release=1.0)
                n = min(len(chord), len(w))
                chord[:n] += w[:n]
        n = min(len(chord), total_samples - pos)
        pad[pos:pos + n] += chord[:n]
        pos += chord_len
    pad = _delay(pad, delay_ms=300, feedback=0.25, wet=0.3)

    # ── Melody (gentle PWM lead) ──
    melody_notes = [
        ('R', 2), ('E4', 1.5), ('R', 0.5),
        ('A4', 1), ('G4', 0.5), ('E4', 0.5), ('R', 2),
        ('R', 1), ('C4', 1), ('D4', 0.5), ('E4', 0.5),
        ('G4', 2), ('E4', 1), ('R', 1),
        ('R', 1), ('D4', 1), ('E4', 0.5), ('G4', 0.5),
        ('A4', 1.5), ('G4', 0.5), ('R', 2),
        ('E4', 1), ('D4', 0.5), ('E4', 0.5),
        ('G4', 1), ('E4', 1), ('D4', 1), ('R', 3),
    ]
    melody = _seq(melody_notes, beat, wave_type='pwm', vol=0.1,
                  attack=0.05, decay=0.1, sustain=0.5, release=0.15,
                  filter_start=2500, filter_end=1000)
    melody = _delay(melody, delay_ms=200, feedback=0.2, wet=0.2)

    # ── Sub bass (sine for warmth) ──
    bass_notes = [
        ('A2', 8), ('F2', 8), ('G2', 8), ('E2', 8),
    ]
    bass = _seq(bass_notes, beat, wave_type='sine', vol=0.2,
                attack=0.05, decay=0.1, sustain=0.8, release=0.3,
                filter_start=10000, filter_end=10000)

    # ── Arp (subtle background movement) ──
    arp_am = _arpeggio([NOTE_FREQ['A3'], NOTE_FREQ['C4'], NOTE_FREQ['E4']], 8 * beat,
                       step_dur=0.18, wave_type='pwm', vol=0.04)
    arp_fm = _arpeggio([NOTE_FREQ['F3'], NOTE_FREQ['A3'], NOTE_FREQ['C4']], 8 * beat,
                       step_dur=0.18, wave_type='pwm', vol=0.04)
    arp_g = _arpeggio([NOTE_FREQ['G3'], NOTE_FREQ['B3'], NOTE_FREQ['D4']], 8 * beat,
                      step_dur=0.18, wave_type='pwm', vol=0.04)
    arp_em = _arpeggio([NOTE_FREQ['E3'], NOTE_FREQ['G3'], NOTE_FREQ['B3']], 8 * beat,
                       step_dur=0.18, wave_type='pwm', vol=0.04)
    arp_dur = int(SAMPLE_RATE * 8 * beat)
    arp = np.zeros(total_samples, dtype=np.float32)
    for i, a in enumerate([arp_am, arp_fm, arp_g, arp_em]):
        start = i * arp_dur
        end = min(start + len(a), total_samples)
        arp[start:end] += a[:end - start]
    arp = _delay(arp, delay_ms=150, feedback=0.3, wet=0.25)

    return _mix(pad, melody, bass, arp) * 0.8


# ─── Music: Gameplay Theme ─────────────────────────────────
def _generate_gameplay_music():
    """High-energy synth — Em, driving beat, saw lead, heavy bass."""
    bpm = 140
    beat = 60.0 / bpm
    total_beats = 32
    total_dur = total_beats * beat
    total_samples = int(SAMPLE_RATE * total_dur)

    # ── Drums ──
    drums = np.zeros(total_samples, dtype=np.float32)
    kick = _drum_kick(0.12)
    snare = _drum_snare(0.1)
    hihat = _drum_hihat(0.04)
    open_hat = _drum_hihat(0.04, open_hat=True)

    for b in range(total_beats):
        pos = int(b * beat * SAMPLE_RATE)
        # Kick on 1, 3
        if b % 4 == 0 or b % 4 == 2:
            drums = _mix(drums, _place(kick, pos, total_samples))
        if b % 4 == 2 and b % 8 == 6:
            drums = _mix(drums, _place(kick, pos + int(beat * 0.5 * SAMPLE_RATE), total_samples))
        # Snare on 2, 4
        if b % 4 == 1 or b % 4 == 3:
            drums = _mix(drums, _place(snare, pos, total_samples))
        # Hi-hats on 8th notes
        for sub in range(2):
            hat_pos = pos + int(sub * beat * 0.5 * SAMPLE_RATE)
            drums = _mix(drums, _place(hihat, hat_pos, total_samples))
        # Open hat accent
        if b % 8 == 0:
            drums = _mix(drums, _place(open_hat, pos + int(beat * 1.75 * SAMPLE_RATE), total_samples))

    # ── Bass (saw + sub) ──
    bass_pattern = [
        ('E2', 0.5), ('E2', 0.25), ('R', 0.25), ('E2', 0.5), ('G2', 0.5),
        ('E2', 0.5), ('E2', 0.25), ('R', 0.25), ('A2', 0.5), ('G2', 0.5),
        ('C2', 0.5), ('C2', 0.25), ('R', 0.25), ('C2', 0.5), ('D2', 0.5),
        ('C2', 0.5), ('C2', 0.25), ('R', 0.25), ('D2', 0.5), ('E2', 0.5),
        ('D2', 0.5), ('D2', 0.25), ('R', 0.25), ('D2', 0.5), ('E2', 0.5),
        ('D2', 0.5), ('D2', 0.25), ('R', 0.25), ('E2', 0.5), ('D2', 0.5),
        ('B2', 0.5), ('B2', 0.25), ('R', 0.25), ('B2', 0.5), ('A2', 0.5),
        ('B2', 0.5), ('B2', 0.25), ('R', 0.25), ('A2', 0.5), ('B2', 0.5),
    ]
    bass_saw = _seq(bass_pattern, beat, wave_type='saw', vol=0.15,
                    attack=0.005, decay=0.03, sustain=0.7, release=0.04,
                    filter_start=800, filter_end=400)
    bass_sub = _seq(bass_pattern, beat, wave_type='sine', vol=0.18,
                    attack=0.01, decay=0.02, sustain=0.9, release=0.05,
                    filter_start=10000, filter_end=10000)

    # ── Lead melody (detuned saw) ──
    lead_notes = [
        ('E4', 0.5), ('E4', 0.25), ('G4', 0.25), ('A4', 0.5), ('B4', 0.5),
        ('E5', 0.5), ('D5', 0.25), ('B4', 0.25), ('A4', 0.5), ('G4', 0.5),
        ('A4', 0.5), ('B4', 0.25), ('A4', 0.25), ('G4', 0.5), ('E4', 0.5),
        ('G4', 0.5), ('A4', 0.25), ('G4', 0.25), ('E4', 0.5), ('R', 0.5),
        ('B4', 0.5), ('B4', 0.25), ('D5', 0.25), ('E5', 0.5), ('D5', 0.5),
        ('B4', 0.5), ('A4', 0.25), ('G4', 0.25), ('E4', 0.5), ('G4', 0.5),
        ('A4', 0.75), ('B4', 0.25), ('A4', 0.5), ('G4', 0.5),
        ('E4', 0.75), ('D4', 0.25), ('E4', 0.5), ('R', 0.5),
    ]
    lead = _seq(lead_notes, beat, wave_type='detune', vol=0.13,
                attack=0.008, decay=0.04, sustain=0.5, release=0.06,
                filter_start=5000, filter_end=2000)
    lead = _delay(lead, delay_ms=100, feedback=0.15, wet=0.15)

    # ── Arp layer (shimmer) ──
    arp1 = _arpeggio(
        [NOTE_FREQ['E4'], NOTE_FREQ['G4'], NOTE_FREQ['B4'], NOTE_FREQ['E5']],
        8 * beat, step_dur=beat * 0.25, wave_type='pwm', vol=0.06
    )
    arp2 = _arpeggio(
        [NOTE_FREQ['C4'], NOTE_FREQ['E4'], NOTE_FREQ['G4'], NOTE_FREQ['C5']],
        8 * beat, step_dur=beat * 0.25, wave_type='pwm', vol=0.06
    )
    arp3 = _arpeggio(
        [NOTE_FREQ['D4'], NOTE_FREQ['Fs4'], NOTE_FREQ['A4'], NOTE_FREQ['D5']],
        8 * beat, step_dur=beat * 0.25, wave_type='pwm', vol=0.06
    )
    arp4 = _arpeggio(
        [NOTE_FREQ['B3'], NOTE_FREQ['D4'], NOTE_FREQ['Fs4'], NOTE_FREQ['B4']],
        8 * beat, step_dur=beat * 0.25, wave_type='pwm', vol=0.06
    )
    arp = np.zeros(total_samples, dtype=np.float32)
    arp_dur = int(SAMPLE_RATE * 8 * beat)
    for i, a in enumerate([arp1, arp2, arp3, arp4]):
        start = i * arp_dur
        end = min(start + len(a), total_samples)
        arp[start:end] += a[:end - start]
    arp = _delay(arp, delay_ms=130, feedback=0.2, wet=0.2)

    # ── Chord stabs ──
    stabs = np.zeros(total_samples, dtype=np.float32)
    stab_chords = [
        ['E3', 'G3', 'B3'],
        ['C3', 'E3', 'G3'],
        ['D3', 'Fs3', 'A3'],
        ['B2', 'D3', 'Fs3'],
    ]
    for i, chord in enumerate(stab_chords):
        pos = int(i * 8 * beat * SAMPLE_RATE)
        stab_len = int(SAMPLE_RATE * beat * 1.5)
        stab = np.zeros(stab_len, dtype=np.float32)
        for note in chord:
            freq = NOTE_FREQ.get(note, 0)
            if freq > 0:
                w = _supersaw(freq, beat * 1.5, vol=0.06, voices=3)
                w = _adsr(w, attack=0.005, decay=0.15, sustain=0.2, release=0.2)
                n = min(len(stab), len(w))
                stab[:n] += w[:n]
        stab = _lp_filter(stab, 2500)
        stabs = _mix(stabs, _place(stab, pos, total_samples))

    return _mix(drums, bass_saw, bass_sub, lead, arp, stabs) * 0.75


# ─── Sound Effects ─────────────────────────────────────────
def _sfx_jump():
    dur = 0.14
    n = int(SAMPLE_RATE * dur)
    w = np.zeros(n, dtype=np.float32)
    phase = 0.0
    for i in range(n):
        f = 250 + 500 * (i / n) ** 0.7
        phase += f / SAMPLE_RATE
        w[i] = np.sin(2 * np.pi * phase) * 0.25
    w += _saw(800, dur, vol=0.06)[:n]
    return _adsr(w, attack=0.005, decay=0.03, sustain=0.3, release=0.04)


def _sfx_land():
    dur = 0.08
    n = int(SAMPLE_RATE * dur)
    body = _noise(dur, vol=0.22)
    body = _lp_filter(body, 1500)
    thud = _sine(80, dur, vol=0.2)
    out = body + thud[:n]
    out *= np.exp(-_t(dur)[:n] * 20).astype(np.float32)
    return out


def _sfx_coin():
    dur = 0.18
    n = int(SAMPLE_RATE * dur)
    w1 = _sine(880, 0.06, vol=0.22)
    w2 = _sine(1320, 0.12, vol=0.18)
    w = np.concatenate([w1, w2])[:n]
    shimmer = _saw(1760, dur, vol=0.04)[:len(w)]
    w += shimmer
    return _adsr(w, attack=0.003, decay=0.03, sustain=0.4, release=0.06)


def _sfx_death():
    dur = 0.45
    n = int(SAMPLE_RATE * dur)
    w = np.zeros(n, dtype=np.float32)
    phase = 0.0
    for i in range(n):
        f = 500 - 440 * (i / n)
        phase += f / SAMPLE_RATE
        w[i] = 0.6 * np.sin(2 * np.pi * phase) + 0.4 * np.sign(np.sin(2 * np.pi * phase))
    w *= 0.18
    noise = _noise(dur, vol=0.08)
    w += noise[:n]
    w = _lp_filter_sweep(w, 4000, 200, resonance=0.3)
    w *= np.exp(-_t(dur)[:n] * 4).astype(np.float32)
    return w


def _sfx_complete():
    notes = [
        (NOTE_FREQ['C5'], 0.1), (NOTE_FREQ['E5'], 0.1),
        (NOTE_FREQ['G5'], 0.1), (NOTE_FREQ['C5'], 0.3),
    ]
    parts = []
    for freq, dur in notes:
        w = _supersaw(freq, dur, vol=0.12, voices=3)
        w = _adsr(w, attack=0.005, decay=0.02, sustain=0.6, release=0.05)
        parts.append(w)
    result = np.concatenate(parts)
    return _delay(result, delay_ms=100, feedback=0.2, wet=0.2)


def _sfx_menu_move():
    w = _sine(520, 0.04, vol=0.12)
    w += _saw(520, 0.04, vol=0.03)
    return _adsr(w, attack=0.003, decay=0.01, sustain=0.3, release=0.01)


def _sfx_menu_select():
    w1 = _sine(523, 0.05, vol=0.14)
    w1 += _saw(523, 0.05, vol=0.04)
    w2 = _sine(784, 0.08, vol=0.14)
    w2 += _saw(784, 0.08, vol=0.04)
    return _adsr(np.concatenate([w1, w2]), attack=0.003, decay=0.02, sustain=0.4, release=0.02)


def _sfx_dash():
    dur = 0.12
    n = int(SAMPLE_RATE * dur)
    sweep = np.zeros(n, dtype=np.float32)
    phase = 0.0
    for i in range(n):
        f = 400 - 300 * (i / n)
        phase += f / SAMPLE_RATE
        sweep[i] = np.sin(2 * np.pi * phase) * 0.12
    noise = _noise(dur, vol=0.15)
    noise = _lp_filter_sweep(noise, 5000, 500)
    out = sweep + noise[:n]
    out *= np.exp(-_t(dur)[:n] * 8).astype(np.float32)
    return out


# ─── Convert to pygame-compatible format ──────────────────
def _to_wav_bytes(audio_data):
    """Convert float32 mono array to WAV bytes (16-bit stereo)."""
    audio_data = np.clip(audio_data, -1.0, 1.0)
    int16 = (audio_data * 32767).astype(np.int16)
    stereo = np.column_stack([int16, int16])
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(stereo.tobytes())
    buf.seek(0)
    return buf


# ─── Audio Manager ─────────────────────────────────────────
class AudioManager:
    """Handles all game audio: music and sound effects."""

    def __init__(self):
        import pygame
        self.pygame = pygame
        self._ready = False
        self.sounds = {}
        self._menu_music = None
        self._gameplay_music = None
        self._current_music = None

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(SAMPLE_RATE, -16, 2, 1024)
            self._ready = True
        except Exception:
            print("[Audio] Could not initialize mixer - running without sound.")
            return

        self._generate_all()

    def _generate_all(self):
        if not self._ready:
            return
        try:
            print("[Audio] Generating synth audio...")
            sfx_map = {
                'jump': _sfx_jump,
                'land': _sfx_land,
                'coin': _sfx_coin,
                'death': _sfx_death,
                'complete': _sfx_complete,
                'menu_move': _sfx_menu_move,
                'menu_select': _sfx_menu_select,
                'dash': _sfx_dash,
            }
            for name, fn in sfx_map.items():
                data = fn()
                wav = _to_wav_bytes(data)
                self.sounds[name] = self.pygame.mixer.Sound(wav)

            self._menu_music = _to_wav_bytes(_generate_menu_music())
            self._gameplay_music = _to_wav_bytes(_generate_gameplay_music())
            print("[Audio] Audio generation complete.")

        except Exception as e:
            print(f"[Audio] Error generating audio: {e}")
            import traceback
            traceback.print_exc()
            self._ready = False

    def play_sfx(self, name):
        if not self._ready:
            return
        snd = self.sounds.get(name)
        if snd:
            snd.set_volume(0.6)
            snd.play()

    def play_menu_music(self):
        if not self._ready or self._menu_music is None:
            return
        if self._current_music == 'menu':
            return
        self._current_music = 'menu'
        try:
            self._menu_music.seek(0)
            self.pygame.mixer.music.load(self._menu_music)
            self.pygame.mixer.music.set_volume(0.4)
            self.pygame.mixer.music.play(-1)
        except Exception:
            pass

    def play_gameplay_music(self):
        if not self._ready or self._gameplay_music is None:
            return
        if self._current_music == 'gameplay':
            return
        self._current_music = 'gameplay'
        try:
            self._gameplay_music.seek(0)
            self.pygame.mixer.music.load(self._gameplay_music)
            self.pygame.mixer.music.set_volume(0.45)
            self.pygame.mixer.music.play(-1)
        except Exception:
            pass

    def stop_music(self):
        if not self._ready:
            return
        self._current_music = None
        try:
            self.pygame.mixer.music.stop()
        except Exception:
            pass

    def set_music_volume(self, vol):
        if not self._ready:
            return
        try:
            self.pygame.mixer.music.set_volume(vol)
        except Exception:
            pass
