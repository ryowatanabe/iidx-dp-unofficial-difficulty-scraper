# HTML上のバージョン略称 → 数値の変換表
# 右辺の None を任意の数値に書き換えてください。
# 変換表にないキーは NULL として保存されます。

VERSION_MAP: dict[str, float | None] = {
    "1st":  1,  # 1st style
    "sub":  1.5,  # substream
    "2nd":  2,  # 2nd style
    "3rd":  3,  # 3rd style
    "4th":  4,  # 4th style
    "5th":  5,  # 5th style
    "6th":  6,  # 6th style
    "7th":  7,  # 7th style
    "8th":  8,  # 8th style
    "9th":  9,  # 9th style
    "10th": 10,  # 10th style
    "RED":  11,  # IIDX RED
    "HSKY": 12,  # HAPPY SKY
    "DD":   13,  # DistorteD
    "GOLD": 14,  # GOLD
    "DJT":  15,  # DJ TROOPERS
    "EMP":  16,  # EMPRESS
    "SIR":  17,  # SIRIUS
    "RA":   18,  # Resort Anthem
    "LC":   19,  # Lincle
    "TRI":  20,  # tricoro
    "SPA":  21,  # SPADA
    "PEN":  22,  # PENDUAL
    "COP":  23,  # copula
    "SINO": 24,  # SINOBUZ
    "CB":   25,  # CANNON BALLERS
    "ROOT": 26,  # Rootage
    "HERO": 27,  # HEROIC VERSE
    "BIS":  28,  # BISTROVER
    "CH":   29,  # CastHour
    "RDT":  30,  # RESIDENT
    "EPO":  31,  # EPOLIS
    "PC":   32,  # Pinky Crush
    "SS":   33,  # Sparkle Shower
}
