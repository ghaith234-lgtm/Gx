package com.holy.dash;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.LinearGradient;
import android.graphics.Paint;
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
            text(c, o.optString("a"), W - pad - colW * 1.15f, yc + 4.5f * v, colW * 0.82f,
                    paint(12f * v, col(o.optString("c")), true, true, Paint.Align.RIGHT));
            // «الكل» and its number drawn apart: the number never trades places with the word, whatever the phone's text direction
            Paint lp = paint(10.5f * v, MUT, false, false, Paint.Align.LEFT);
            float lw = lp.measureText("الكل");
            float bw = text(c, o.optString("b"), pad, yc + 4.5f * v, colW * 0.95f - lw - 5f * d, paint(11.5f * v, MUT, false, true, Paint.Align.LEFT));
            c.drawText("الكل", pad + bw + 5f * d, yc + 4.5f * v, lp);
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
}
