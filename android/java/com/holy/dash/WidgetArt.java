package com.holy.dash;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.LinearGradient;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.RectF;
import android.graphics.Shader;
import android.graphics.Typeface;

import org.json.JSONArray;
import org.json.JSONObject;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

/**
 * 📱 app 2.0 (dashboard v3.36.32) — the home-screen widget drawn like the dashboard's card «B», in the interface's purple (the owner 13-11:
 * «اتسويه مثل الكروت وافضل كرت b واتضيف عليه ربح البارحه واخر اسبوع واخر شهر · خلي لون الويدجيت مثل لون البنفسجي الي بالواجهة»).
 * HolyWidget.render / HolyWidget.speak hand over to here; everything else in HolyWidget (fetch · key · cache · tap opens Holy behind the
 * lock · pin) is the 1.9 bytecode unchanged. Reads the dashboard's /api/app/widget: «kb» = the six numbers (today · yesterday · last 7 days ·
 * last 30 days · this month · total) — or the 1.9 «k» (three) from an older dashboard · «bots» = {e, s, on, a, b, c, t}.
 * 🪙 app 2.3: renderPx draws the prices widget (HolyPxWidget) from the same answer's «px» = [{s, p, ch, sp}] · the bots' «b» (all their
 * days) is no longer drawn.
 * Display only: no keys, no balances, no orders.
 */
final class WidgetArt {
    private static final int BG_TOP = 0xFF1B1233;
    private static final int BG_BOT = 0xFF0F0B1D;
    private static final int VIO = 0xFFA78BFA;
    private static final int VIO_T = 0xFFC4B5FD;
    private static final int EDGE = 0x55A78BFA;
    private static final int SEP = 0x38A78BFA;
    private static final int MUT = 0xFFA39BC4;
    private static final int TX = 0xFFF3F0FF;
    private static final int UP = 0xFF34D399;
    private static final int DN = 0xFFF87171;
    private static final int WARN = 0xFFF4C95D;

    private WidgetArt() {
    }

    static int col(String c) {
        if ("u".equals(c)) return UP;
        if ("d".equals(c)) return DN;
        return TX;
    }

    /** the bot kind's colour (the cards' own: ♾️ purple · 🎚️ blue · ➕ pink · 🪜 / 🔁 cyan · DCA amber · 💹 green) */
    static int kind(String t, String e) {
        if (t == null) t = "";
        if (t.equals("grid_range")) return 0xFF60A5FA;
        if (t.equals("grid_plus")) return 0xFFF472B6;
        if (t.equals("grid_step") || t.equals("rec_buy") || t.equals("rec_sell")) return 0xFF22D3EE;
        if (t.equals("dca") || t.equals("dca_buy")) return 0xFFF4C95D;
        if (t.equals("rec_va")) return 0xFF34D399;
        return VIO;
    }

    private static Paint paint(float size, int color, boolean bold, boolean mono, Paint.Align align) {
        Paint p = new Paint(Paint.ANTI_ALIAS_FLAG | Paint.SUBPIXEL_TEXT_FLAG);
        p.setTextSize(size);
        p.setColor(color);
        p.setTypeface(mono ? Typeface.create(Typeface.MONOSPACE, bold ? Typeface.BOLD : Typeface.NORMAL)
                : (bold ? Typeface.DEFAULT_BOLD : Typeface.DEFAULT));
        p.setTextAlign(align);
        return p;
    }

    /** draws s, shrinking the font until it fits in max px (never below 6 px) */
    private static float text(Canvas c, String s, float x, float y, float max, Paint p) {
        if (s == null) s = "";
        float sz = p.getTextSize();
        while (sz > 6f && p.measureText(s) > max) {
            sz -= 0.5f;
            p.setTextSize(sz);
        }
        c.drawText(s, x, y, p);
        return p.measureText(s);
    }

    static Bitmap render(Context ctx, JSONObject j, long t, int wDp, int hDp, float d) {
        int W = Math.max(1, Math.min(Math.round(wDp * d), 1400));
        int H = Math.max(1, Math.min(Math.round(hDp * d), 1100));
        Bitmap bm = Bitmap.createBitmap(W, H, Bitmap.Config.ARGB_8888);
        Canvas c = new Canvas(bm);
        // v = the vertical unit: the full card needs 122 dp of height; a widget made smaller shrinks the letters and rows with it
        float v = d * Math.max(0.62f, Math.min(1f, hDp / 122f));
        float pad = 14f * d;
        float padV = 14f * v;
        // the card: dark purple · the interface's purple edge · the coloured bar on the reading side (like card B)
        Paint bg = new Paint(Paint.ANTI_ALIAS_FLAG);
        bg.setShader(new LinearGradient(W, 0, 0, H, BG_TOP, BG_BOT, Shader.TileMode.CLAMP));
        RectF all = new RectF(0, 0, W, H);
        c.drawRoundRect(all, 20f * d, 20f * d, bg);
        Paint edge = new Paint(Paint.ANTI_ALIAS_FLAG);
        edge.setStyle(Paint.Style.STROKE);
        edge.setStrokeWidth(Math.max(1f, d));
        edge.setColor(EDGE);
        c.drawRoundRect(new RectF(0.5f, 0.5f, W - 0.5f, H - 0.5f), 20f * d, 20f * d, edge);
        Paint bar = new Paint(Paint.ANTI_ALIAS_FLAG);
        bar.setShader(new LinearGradient(0, padV, 0, H - padV, VIO, 0x33A78BFA, Shader.TileMode.CLAMP));
        c.drawRoundRect(new RectF(W - 4f * d, padV, W - 1f * d, H - padV), 2f * d, 2f * d, bar);

        // the head: «Holy» · ● running / bots · HH:mm (⚠️ when the last answer is older than 15 minutes)
        float yh = padV + 14f * v;
        c.drawText("Holy", W - pad, yh, paint(16f * v, VIO_T, true, false, Paint.Align.RIGHT));
        boolean stale = t > 0 && System.currentTimeMillis() - t > 900000L;
        String hm = t > 0 ? new SimpleDateFormat("HH:mm", Locale.US).format(new Date(t)) : "";
        if (j == null) {
            Paint m1 = paint(12.5f * v, TX, false, false, Paint.Align.RIGHT);
            text(c, "افتح Holy وادخل إلى لوحتك مرة واحدة", W - pad, yh + 30f * v, W - 2 * pad, m1);
            Paint m2 = paint(11f * v, MUT, false, false, Paint.Align.RIGHT);
            text(c, "ليرتبط الجهاز وتظهر بوتاتك وأرباحك هنا", W - pad, yh + 50f * v, W - 2 * pad, m2);
            if (H >= yh + 50f * v + 30f * v) text(c, "اضغط للفتح", W - pad, H - 8f * v, W - 2 * pad, paint(11f * v, MUT, false, false, Paint.Align.RIGHT));
            return bm;
        }
        int run = j.optInt("run", 0), n = j.optInt("n", 0);
        String st = (stale ? "⚠️ " : "") + run + "/" + n + " يعمل" + (hm.isEmpty() ? "" : " · " + hm);
        Paint sp = paint(11.5f * v, stale ? WARN : MUT, false, false, Paint.Align.LEFT);
        float sw = text(c, st, pad, yh, W * 0.55f, sp);
        Paint dot = new Paint(Paint.ANTI_ALIAS_FLAG);
        dot.setColor(stale ? WARN : (run > 0 ? UP : DN));
        c.drawCircle(pad + sw + 7f * d, yh - 4f * v, 3.2f * v, dot);

        // the numbers: three columns, a thin purple line between them (like card B's bar of three)
        JSONArray k = j.optJSONArray("kb");
        if (k == null) k = j.optJSONArray("k");
        int nk = k == null ? 0 : Math.min(k.length(), 6);
        float y0 = yh + 12f * v;
        float colW = (W - 2 * pad) / 3f;
        float rowH = 37f * v;
        int rows = (nk + 2) / 3;
        Paint sep = new Paint(Paint.ANTI_ALIAS_FLAG);
        sep.setColor(SEP);
        sep.setStrokeWidth(Math.max(1f, d));
        for (int cI = 1; cI < 3 && rows > 0; cI++) {
            float x = W - pad - cI * colW;
            c.drawLine(x, y0 + 2f * v, x, y0 + rows * rowH - 6f * v, sep);
        }
        for (int i = 0; i < nk; i++) {
            JSONArray e = k.optJSONArray(i);
            if (e == null) continue;
            int r = i / 3, ci = i % 3;
            float xr = W - pad - ci * colW - (ci == 0 ? 0f : 9f * d);
            float wmax = colW - (ci == 0 ? 9f * d : 14f * d);
            float yl = y0 + r * rowH + 11f * v;
            text(c, e.optString(0), xr, yl, wmax, paint(10.5f * v, MUT, false, false, Paint.Align.RIGHT));
            text(c, e.optString(1), xr, yl + 18f * v, wmax, paint(15f * v, col(e.optString(2)), true, true, Paint.Align.RIGHT));
        }
        float ydiv = y0 + rows * rowH;

        // the bots: the kind's bar · emoji + coin · running dot · today · all its days
        JSONArray b = j.optJSONArray("bots");
        int nb = b == null ? 0 : b.length();
        float rh = 21f * v;
        float foot = 18f * v;                       // the last line («اضغط للفتح») — its baseline sits 8v above the bottom
        float room = H - ydiv - 4f * v - foot;      // what is left for bot rows between the numbers and the last line
        int fit = (int) Math.floor(room / rh);
        int show = Math.max(0, Math.min(nb, fit));
        boolean footer = H - ydiv >= foot + 2f * v;
        if (rows > 0 && footer) c.drawLine(pad, ydiv, W - pad, ydiv, sep);
        Paint kb = new Paint(Paint.ANTI_ALIAS_FLAG);
        Paint on = new Paint(Paint.ANTI_ALIAS_FLAG);
        for (int i = 0; i < show; i++) {
            JSONObject o = b.optJSONObject(i);
            if (o == null) continue;
            float yc = ydiv + 4f * v + i * rh + rh / 2f;
            kb.setColor(kind(o.optString("t"), o.optString("e")));
            c.drawRoundRect(new RectF(W - pad - 3f * d, yc - 7f * v, W - pad, yc + 7f * v), 1.5f * d, 1.5f * d, kb);
            Paint np = paint(12.5f * v, TX, false, false, Paint.Align.RIGHT);
            float nw = text(c, o.optString("e") + " " + o.optString("s"), W - pad - 9f * d, yc + 4.5f * v, colW * 1.05f - 20f * d, np);
            on.setColor(o.optInt("on", 0) == 1 ? UP : DN);
            c.drawCircle(W - pad - 9f * d - nw - 7f * d, yc, 3f * v, on);
            // 🗑️ app 2.3 (the owner 21-11: «الاول زيل منه الكل»): today's number only, at the far end of the row
            text(c, o.optString("a"), pad, yc + 4.5f * v, colW * 1.1f, paint(12f * v, col(o.optString("c")), true, true, Paint.Align.LEFT));
        }
        if (nb == 0 && fit > 0) {
            text(c, "لا توجد بوتات بعد", W - pad, ydiv + 4f * v + rh / 2f + 4.5f * v, W - 2 * pad,
                    paint(12f * v, MUT, false, false, Paint.Align.RIGHT));
        }
        if (footer) {
            int rest = nb - show;
            String more = show == 0 && nb > 0 ? (nb == 1 ? "بوت واحد" : nb == 2 ? "بوتان" : nb + " بوتات") + " — اضغط للفتح"
                    : rest <= 0 ? "اضغط للفتح"
                    : (rest == 1 ? "وبوت آخر" : rest == 2 ? "وبوتان آخران" : "و " + rest + " بوتات أخرى") + " — اضغط للفتح";
            text(c, more, W - pad, H - 8f * v, W - 2 * pad, paint(11f * v, MUT, false, false, Paint.Align.RIGHT));
        }
        return bm;
    }

    /** the same summary in words for TalkBack */
    static String speak(JSONObject j) {
        if (j == null) return "Holy — افتح Holy وادخل إلى لوحتك مرة واحدة";
        StringBuilder s = new StringBuilder("Holy — ");
        s.append(j.optInt("run", 0)).append(" من ").append(j.optInt("n", 0)).append(" بوتات تعمل");
        JSONArray k = j.optJSONArray("kb");
        if (k == null) k = j.optJSONArray("k");
        for (int i = 0; k != null && i < Math.min(k.length(), 6); i++) {
            JSONArray e = k.optJSONArray(i);
            if (e != null) s.append(" · ").append(e.optString(0)).append(" ").append(e.optString(1));
        }
        JSONArray b = j.optJSONArray("bots");
        for (int i = 0; b != null && i < Math.min(b.length(), 6); i++) {
            JSONObject o = b.optJSONObject(i);
            if (o != null) s.append(" · ").append(o.optString("s")).append(" ").append(o.optString("a"));
        }
        return s.toString();
    }

    // ---------- 🪙 the prices widget (app 2.3) ----------

    /** the coin's colour (its own, for the best known coins · a steady one from its name for the rest) */
    static int coinColor(String s) {
        switch (s == null ? "" : s) {
            case "BTC": return 0xFFF7931A;
            case "ETH": return 0xFF627EEA;
            case "SOL": return 0xFF9945FF;
            case "XRP": return 0xFF23292F;
            case "DOGE": return 0xFFC2A633;
            case "LINK": return 0xFF2A5ADA;
            case "BNB": return 0xFFF3BA2F;
            case "ADA": return 0xFF0033AD;
            case "TRX": return 0xFFFF060A;
            case "AVAX": return 0xFFE84142;
            case "SUI": return 0xFF4DA2FF;
            case "LTC": return 0xFF345D9D;
            case "DOT": return 0xFFE6007A;
            case "TON": return 0xFF0098EA;
            case "SHIB": return 0xFFE42D04;
            case "PEPE": return 0xFF4C8F3C;
            case "BCH": return 0xFF0AC18E;
            case "XLM": return 0xFF3E5BA9;
            default: break;
        }
        int[] pal = {0xFF8B5CF6, 0xFF0EA5E9, 0xFF14B8A6, 0xFFF59E0B, 0xFFEC4899, 0xFF22C55E, 0xFF6366F1, 0xFFEF4444};
        return pal[((s == null ? 0 : s.hashCode()) & 0x7fffffff) % pal.length];
    }

    /** the coin's shape: a round badge in its colour with a simple mark drawn from lines (no logo pictures) — on an 18-unit grid */
    static void badge(Canvas c, String s, float cx, float cy, float r) {
        Paint f = new Paint(Paint.ANTI_ALIAS_FLAG);
        f.setColor(coinColor(s));
        c.drawCircle(cx, cy, r, f);
        if ("XRP".equals(s)) {
            Paint ring = new Paint(Paint.ANTI_ALIAS_FLAG);
            ring.setStyle(Paint.Style.STROKE);
            ring.setStrokeWidth(Math.max(1f, r / 9f));
            ring.setColor(0xFF5B6470);
            c.drawCircle(cx, cy, r - r / 18f, ring);
        }
        final float k = r / 9f, x0 = cx - r, y0 = cy - r;
        Paint w = new Paint(Paint.ANTI_ALIAS_FLAG);
        w.setColor(0xFFFFFFFF);
        Paint st = new Paint(Paint.ANTI_ALIAS_FLAG);
        st.setColor(0xFFFFFFFF);
        st.setStyle(Paint.Style.STROKE);
        st.setStrokeWidth(1.6f * k);
        st.setStrokeCap(Paint.Cap.ROUND);
        st.setStrokeJoin(Paint.Join.ROUND);
        Path p = new Path();
        String m = s == null ? "" : s;
        if (m.equals("ETH")) {
            poly(p, x0, y0, k, 9, 2.6f, 13.4f, 9.4f, 9, 12, 4.6f, 9.4f);
            c.drawPath(p, w);
            p.reset();
            poly(p, x0, y0, k, 9, 12.9f, 13.4f, 10.3f, 9, 15.6f, 4.6f, 10.3f);
            w.setAlpha(190);
            c.drawPath(p, w);
        } else if (m.equals("SOL")) {
            for (int i = 0; i < 3; i++) {
                float y = 5.6f + i * 2.7f;
                if (i == 1) poly(p, x0, y0, k, 4.2f, y, 12.2f, y, 13.6f, y + 1.4f, 5.6f, y + 1.4f);
                else poly(p, x0, y0, k, 5.6f, y, 13.6f, y, 12.2f, y + 1.4f, 4.2f, y + 1.4f);
            }
            c.drawPath(p, w);
        } else if (m.equals("XRP")) {
            p.moveTo(x0 + 4.6f * k, y0 + 5f * k);
            p.lineTo(x0 + 7.4f * k, y0 + 7.8f * k);
            p.quadTo(x0 + 9f * k, y0 + 9.3f * k, x0 + 10.6f * k, y0 + 7.8f * k);
            p.lineTo(x0 + 13.4f * k, y0 + 5f * k);
            p.moveTo(x0 + 4.6f * k, y0 + 13f * k);
            p.lineTo(x0 + 7.4f * k, y0 + 10.2f * k);
            p.quadTo(x0 + 9f * k, y0 + 8.7f * k, x0 + 10.6f * k, y0 + 10.2f * k);
            p.lineTo(x0 + 13.4f * k, y0 + 13f * k);
            st.setStrokeWidth(1.5f * k);
            c.drawPath(p, st);
        } else if (m.equals("LINK")) {
            poly(p, x0, y0, k, 9, 3.8f, 13.5f, 6.4f, 13.5f, 11.6f, 9, 14.2f, 4.5f, 11.6f, 4.5f, 6.4f);
            st.setStrokeWidth(1.7f * k);
            c.drawPath(p, st);
        } else if (m.equals("BNB")) {
            float[][] dm = {{9, 5.6f, 2}, {5.6f, 9, 2}, {12.4f, 9, 2}, {9, 12.4f, 2}, {9, 9, 1.1f}};
            for (float[] q : dm) poly(p, x0, y0, k, q[0], q[1] - q[2], q[0] + q[2], q[1], q[0], q[1] + q[2], q[0] - q[2], q[1]);
            c.drawPath(p, w);
        } else if (m.equals("ADA")) {
            float[][] dt = {{9, 4}, {9, 14}, {4.7f, 6.5f}, {13.3f, 6.5f}, {4.7f, 11.5f}, {13.3f, 11.5f}};
            for (float[] q : dt) c.drawCircle(x0 + q[0] * k, y0 + q[1] * k, 1.05f * k, w);
            c.drawCircle(cx, cy, 2f * k, w);
        } else if (m.equals("AVAX")) {
            poly(p, x0, y0, k, 9, 4, 13.8f, 13, 10.9f, 13, 9, 9.4f, 7.1f, 13, 4.2f, 13);
            c.drawPath(p, w);
        } else if (m.equals("SUI")) {
            p.moveTo(x0 + 9f * k, y0 + 3.6f * k);
            p.cubicTo(x0 + 11.6f * k, y0 + 7f * k, x0 + 12.6f * k, y0 + 8.6f * k, x0 + 12.6f * k, y0 + 10.6f * k);
            p.cubicTo(x0 + 12.6f * k, y0 + 15.4f * k, x0 + 5.4f * k, y0 + 15.4f * k, x0 + 5.4f * k, y0 + 10.6f * k);
            p.cubicTo(x0 + 5.4f * k, y0 + 8.6f * k, x0 + 6.4f * k, y0 + 7f * k, x0 + 9f * k, y0 + 3.6f * k);
            p.close();
            c.drawPath(p, w);
        } else if (m.equals("DOT")) {
            c.drawCircle(cx, cy, 2.2f * k, w);
            c.drawOval(new RectF(x0 + 6.4f * k, y0 + 3.3f * k, x0 + 11.6f * k, y0 + 5.9f * k), w);
            c.drawOval(new RectF(x0 + 6.4f * k, y0 + 12.1f * k, x0 + 11.6f * k, y0 + 14.7f * k), w);
        } else if (m.equals("TRX")) {
            poly(p, x0, y0, k, 4, 5, 14.2f, 6.6f, 8.6f, 14);
            p.moveTo(x0 + 4f * k, y0 + 5f * k);
            p.lineTo(x0 + 11.2f * k, y0 + 8.7f * k);
            p.lineTo(x0 + 14.2f * k, y0 + 6.6f * k);
            st.setStrokeWidth(1.2f * k);
            c.drawPath(p, st);
        } else {
            // a letter: ₿ drawn as B with its two strokes · Ð · Ł · otherwise the first letter
            String g = m.equals("BTC") ? "B" : m.equals("DOGE") ? "Ð" : m.equals("LTC") ? "Ł" : (m.isEmpty() ? "?" : m.substring(0, 1));
            Paint t = paint(r * (m.equals("BTC") ? 1.2f : 1.05f), 0xFFFFFFFF, true, false, Paint.Align.CENTER);
            c.drawText(g, cx, cy + r * 0.42f, t);
            if (m.equals("BTC")) {
                Paint bl = new Paint(Paint.ANTI_ALIAS_FLAG);
                bl.setColor(0xFFFFFFFF);
                bl.setStrokeWidth(1.2f * k);
                for (float dx : new float[]{-1.1f, 1.1f}) {
                    c.drawLine(cx + dx * k, cy - r * 0.62f, cx + dx * k, cy - r * 0.42f, bl);
                    c.drawLine(cx + dx * k, cy + r * 0.48f, cx + dx * k, cy + r * 0.66f, bl);
                }
            }
        }
    }

    /** shrinks p until s fits in max px (never below 6 px) — measures only */
    private static float fit(String s, float max, Paint p) {
        float sz = p.getTextSize();
        while (sz > 6f && p.measureText(s) > max) {
            sz -= 0.5f;
            p.setTextSize(sz);
        }
        return p.measureText(s);
    }

    private static void poly(Path p, float x0, float y0, float k, float... xy) {
        p.moveTo(x0 + xy[0] * k, y0 + xy[1] * k);
        for (int i = 2; i + 1 < xy.length; i += 2) p.lineTo(x0 + xy[i] * k, y0 + xy[i + 1] * k);
        p.close();
    }

    /** the line of the last 24 hours (points 0…1000 from the dashboard) with a soft fill under it */
    private static void spark(Canvas c, JSONArray sp, boolean up, float l, float t, float r, float b, float d) {
        int n = sp == null ? 0 : sp.length();
        if (n < 2 || r - l < 4 || b - t < 3) return;
        int col = up ? UP : DN;
        Path line = new Path();
        for (int i = 0; i < n; i++) {
            float x = l + (r - l) * i / (n - 1f);
            float y = b - (b - t) * (float) Math.max(0, Math.min(1000, sp.optDouble(i, 500))) / 1000f;
            if (i == 0) line.moveTo(x, y);
            else line.lineTo(x, y);
        }
        Path fill = new Path(line);
        fill.lineTo(r, b);
        fill.lineTo(l, b);
        fill.close();
        Paint fp = new Paint(Paint.ANTI_ALIAS_FLAG);
        fp.setShader(new LinearGradient(0, t, 0, b, (col & 0x00FFFFFF) | 0x52000000, col & 0x00FFFFFF, Shader.TileMode.CLAMP));
        c.drawPath(fill, fp);
        Paint lp = new Paint(Paint.ANTI_ALIAS_FLAG);
        lp.setStyle(Paint.Style.STROKE);
        lp.setStrokeWidth(Math.max(1f, 1.5f * d));
        lp.setStrokeJoin(Paint.Join.ROUND);
        lp.setColor(col);
        c.drawPath(line, lp);
    }

    static Bitmap renderPx(Context ctx, JSONObject j, long t, int wDp, int hDp, float d) {
        int W = Math.max(1, Math.min(Math.round(wDp * d), 1400));
        int H = Math.max(1, Math.min(Math.round(hDp * d), 1400));
        Bitmap bm = Bitmap.createBitmap(W, H, Bitmap.Config.ARGB_8888);
        Canvas c = new Canvas(bm);
        float v = d * Math.max(0.7f, Math.min(1f, hDp / 120f));
        float pad = 14f * d, padV = 12f * v;
        Paint bg = new Paint(Paint.ANTI_ALIAS_FLAG);
        bg.setShader(new LinearGradient(W, 0, 0, H, BG_TOP, BG_BOT, Shader.TileMode.CLAMP));
        c.drawRoundRect(new RectF(0, 0, W, H), 20f * d, 20f * d, bg);
        Paint edge = new Paint(Paint.ANTI_ALIAS_FLAG);
        edge.setStyle(Paint.Style.STROKE);
        edge.setStrokeWidth(Math.max(1f, d));
        edge.setColor(EDGE);
        c.drawRoundRect(new RectF(0.5f, 0.5f, W - 0.5f, H - 0.5f), 20f * d, 20f * d, edge);
        Paint bar = new Paint(Paint.ANTI_ALIAS_FLAG);
        bar.setShader(new LinearGradient(0, padV, 0, H - padV, VIO, 0x33A78BFA, Shader.TileMode.CLAMP));
        c.drawRoundRect(new RectF(W - 4f * d, padV, W - 1f * d, H - padV), 2f * d, 2f * d, bar);

        // the head: «Holy الأسعار» · HH:mm (⚠️ when the last answer is older than 15 minutes)
        float yh = padV + 13f * v;
        Paint hp = paint(15f * v, VIO_T, true, false, Paint.Align.RIGHT);
        c.drawText("Holy", W - pad, yh, hp);
        float hw = hp.measureText("Holy");
        c.drawText("الأسعار", W - pad - hw - 6f * d, yh, paint(11f * v, MUT, false, false, Paint.Align.RIGHT));
        boolean stale = t > 0 && System.currentTimeMillis() - t > 900000L;
        String hm = t > 0 ? new SimpleDateFormat("HH:mm", Locale.US).format(new Date(t)) : "";
        if (!hm.isEmpty()) text(c, (stale ? "⚠️ " : "") + hm, pad, yh, W * 0.4f, paint(11f * v, stale ? WARN : MUT, false, true, Paint.Align.LEFT));
        JSONArray px = j == null ? null : j.optJSONArray("px");
        if (j == null || px == null || px.length() == 0) {
            String m1 = j == null ? "افتح Holy وادخل إلى لوحتك مرة واحدة" : px == null ? "حدّث لوحتك لتظهر الأسعار هنا" : "أضف عملات إلى شريط الأسعار في اللوحة";
            text(c, m1, W - pad, yh + 28f * v, W - 2 * pad, paint(12.5f * v, TX, false, false, Paint.Align.RIGHT));
            if (H >= yh + 28f * v + 30f * v) text(c, "اضغط للفتح", W - pad, H - 8f * v, W - 2 * pad, paint(11f * v, MUT, false, false, Paint.Align.RIGHT));
            return bm;
        }
        // the tiles: as many as fit (≈ 100 wide · 63 high) — a bigger widget holds more
        int cols = Math.max(2, (int) Math.floor((wDp - 24) / 100f));
        int rows = Math.max(1, (int) Math.floor((hDp - 58) / 63f));
        int fit = Math.min(px.length(), cols * rows);
        if (fit < cols * rows) rows = Math.max(1, (fit + cols - 1) / cols);
        float gx = 12f * d, gap = 7f * d;
        float top = yh + 9f * v, foot = 17f * v;
        float bottom = H - foot - 2f * v;
        float tw = (W - 2 * gx - (cols - 1) * gap) / cols;
        float th = Math.min(96f * v, (bottom - top - (rows - 1) * gap) / rows);   // fewer coins ⇒ taller tiles (the widget stays full)
        Paint tile = new Paint(Paint.ANTI_ALIAS_FLAG);
        tile.setColor(0x0DA78BFA);
        Paint tileEdge = new Paint(Paint.ANTI_ALIAS_FLAG);
        tileEdge.setStyle(Paint.Style.STROKE);
        tileEdge.setStrokeWidth(Math.max(1f, d));
        tileEdge.setColor(SEP);
        for (int i = 0; i < fit; i++) {
            JSONObject o = px.optJSONObject(i);
            if (o == null) continue;
            int r = i / cols, ci = i % cols;
            float R = W - gx - ci * (tw + gap), L = R - tw, T = top + r * (th + gap), B = T + th;
            RectF box = new RectF(L, T, R, B);
            c.drawRoundRect(box, 12f * d, 12f * d, tile);
            c.drawRoundRect(box, 12f * d, 12f * d, tileEdge);
            String s = o.optString("s");
            double ch = o.optDouble("ch", 0);
            boolean up = ch >= 0;
            float br = 8f * v, by = T + 6f * v + br;
            badge(c, s, R - 8f * d - br, by, br);
            Paint np = paint(12.5f * v, TX, true, false, Paint.Align.RIGHT);
            float nw = text(c, s, R - 8f * d - 2 * br - 5f * d, by + 4.3f * v, tw * 0.42f, np);
            // the change: a small pill on the far side
            String cs = (up ? "▲" : "▼") + String.format(Locale.US, "%.2f%%", Math.abs(ch));
            Paint cp = paint(9.5f * v, up ? UP : DN, true, true, Paint.Align.LEFT);
            float room = tw - 16f * d - 2 * br - 5f * d - nw - 6f * d;
            float cw = fit(cs, Math.max(10f * d, room - 8f * d), cp);
            Paint pill = new Paint(Paint.ANTI_ALIAS_FLAG);
            pill.setColor(((up ? UP : DN) & 0x00FFFFFF) | 0x22000000);
            c.drawRoundRect(new RectF(L + 8f * d, by - 6.4f * v, L + 8f * d + cw + 8f * d, by + 6.4f * v), 6f * d, 6f * d, pill);
            c.drawText(cs, L + 8f * d + 4f * d, by + 3.6f * v, cp);
            float yp = by + br + 14f * v;
            text(c, o.optString("p"), R - 8f * d, yp, tw - 16f * d, paint(12.5f * v, TX, true, true, Paint.Align.RIGHT));
            spark(c, o.optJSONArray("sp"), up, L + 6f * d, yp + 4f * v, R - 6f * d, B - 4f * v, d);
        }
        int rest = px.length() - fit;
        String more = rest <= 0 ? "اضغط للفتح" : (rest == 1 ? "وعملة أخرى" : rest == 2 ? "وعملتان أخريان" : "و " + rest + " عملات أخرى") + " — اضغط للفتح";
        text(c, more, W - pad, H - 7f * v, W - 2 * pad, paint(10.5f * v, MUT, false, false, Paint.Align.RIGHT));
        return bm;
    }

    /** the prices in words for TalkBack */
    static String speakPx(JSONObject j) {
        if (j == null) return "Holy الأسعار — افتح Holy وادخل إلى لوحتك مرة واحدة";
        JSONArray px = j.optJSONArray("px");
        if (px == null || px.length() == 0) return "Holy الأسعار — لا توجد عملات بعد";
        StringBuilder s = new StringBuilder("Holy الأسعار");
        for (int i = 0; i < Math.min(px.length(), 20); i++) {
            JSONObject o = px.optJSONObject(i);
            if (o == null) continue;
            double ch = o.optDouble("ch", 0);
            s.append(" · ").append(o.optString("s")).append(" ").append(o.optString("p"))
                    .append(ch >= 0 ? " ارتفع " : " انخفض ").append(String.format(Locale.US, "%.2f", Math.abs(ch))).append("%");
        }
        return s.toString();
    }

}
