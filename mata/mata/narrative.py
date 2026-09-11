"""Narasi untuk tiap flag: template deterministik (default, tanpa API)
atau LLM opsional (jika config.llm.enabled — fallback ke template jika gagal).

Prinsip: penjelasan selalu menyebut ANGKA + dasar prinsip PBJ (bukan vonis).
"""
import json

PRINSIP = "Prinsip pengadaan: terbuka, transparan, kompetitif, akuntabel, dan bersih (Perpres 12/2021)."


def _tpl_d1(m):
    return (
        f"Nilai proyek ({m['nilai']:,.0f}) menyimpang +{m['deviasi']*100:.0f}% dari harga "
        f"referensi katalog/peer ({m['referensi']:,.0f}). Penyimpangan sebesar ini dapat "
        f"merujuk pada HPS yang tidak wajar atau spesifikasi yang digoreksi. {PRINSIP}"
    )


def _tpl_d2(m):
    return (
        f"Penyedia {m['vendor']} mengambil {m['porsi']*100:.0f}% nilai pengadaan "
        f"({m['jumlah_proyek']} proyek). Dominasi seperti ini mengikis kompetisi dan "
        f"meningkatkan risiko pengaturan pemenang. {PRINSIP}"
    )


def _tpl_d3(m):
    return (
        f"{m['jumlah_kontrak']} kontrak besar (total {m['total_jendela']:,.0f}) terpusat pada "
        f"jendela {m['jendela']} — {m['rasio']}x median bulan lain. Keroyokan akhir tahun "
        f"adalah pola klasik penyerapan anggaran; perlu ditelusuri urgensi dan dasar "
        f"pemilihannya. {PRINSIP}"
    )


def _tpl_d4(m):
    return (
        f"{m['vendor']} dengan riwayat {len(m['riwayat'])} proyek kecil (terbesar "
        f"{max(v for _, v in m['riwayat']):,.0f}) memenangkan kontrak {m['kontrak_besar']:,.0f}. "
        f"Kesenjangan kapabilitas dan nilai kontrak perlu diverifikasi (kepemilikan, "
        f"pengalaman, modal). {PRINSIP}"
    )


def _tpl_d6(m):
    return (
        f"Nilai identik {m['nilai']:,.0f} muncul {m['jumlah']}x pada proyek/instansi berbeda. "
        f"Bisa janggal (pola anggaran yang disamakan) — perlu diperiksa dasar penetapannya. "
        f"{PRINSIP}"
    )


TEMPLATES = {"D1": _tpl_d1, "D2": _tpl_d2, "D3": _tpl_d3, "D4": _tpl_d4, "D6": _tpl_d6}

RECOMMENDATIONS = {
    "D1": "Permohonkan dokumen HPS, RAB, dan dasar penetapan harga ke PPK; bandingkan dengan harga e-Katalog item sejenis.",
    "D2": "Permohonkan rekapitulasi pemenang per penyedia; periksa indikasi subkontrak/afiliasi; laporkan ke APIP bila indikasi diperkuat.",
    "D3": "Permohonkan dokumen kebutuhan & jadwal; periksa apakah proyek bersifat darurat atau rencana yang dimundurkan.",
    "D4": "Permohonkan dokumen kualifikasi penyedia; periksa rekam jejak (e-kontrak) dan afiliasi.",
    "D6": "Permohonkan dasar penetapan nilai; bandingkan dengan RAB proyek sejenis.",
}


def _llm_explain(flag, cfg):
    try:
        import requests
        llm = cfg.get("llm", {})
        resp = requests.post(
            f"{llm['base_url']}/chat/completions",
            headers={"Authorization": f"Bearer {llm['api_key']}"},
            json={
                "model": llm.get("model", "gpt-4o-mini"),
                "temperature": 0.2,
                "messages": [
                    {"role": "system", "content":
                        "Kamu analis pengadaan. Tulis 2-3 kalimat penjelasan netral dalam "
                        "bahasa Indonesia untuk indikasi anomali berikut. Gunakan angka yang "
                        "diberikan. Jangan memvonis; gunakan kata 'indikasi'."},
                    {"role": "user", "content": json.dumps(
                        {"rule": flag.rule_id, "metrics": flag.metrics,
                         "evidence": flag.evidence}, ensure_ascii=False)},
                ],
            },
            timeout=30,
        )
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception:  # noqa: BLE001 — selalu fallback ke template
        return TEMPLATES.get(flag.rule_id, lambda m: "")(flag.metrics)


def explain(flag, cfg):
    if cfg.get("llm", {}).get("enabled") and cfg.get("llm", {}).get("api_key"):
        flag.explanation = _llm_explain(flag, cfg)
    else:
        flag.explanation = TEMPLATES.get(flag.rule_id, lambda m: "")(flag.metrics)
    flag.recommendation = RECOMMENDATIONS.get(flag.rule_id, "Perdalam pemeriksaan dokumen pendukung.")
    return flag
