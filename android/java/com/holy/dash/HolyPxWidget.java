package com.holy.dash;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.widget.RemoteViews;

import org.json.JSONObject;

/**
 * 🪙 app 2.3 (dashboard v3.36.70) — the second home-screen widget: the ticker's coins in tiles (the coin's badge · name · 24-hour change ·
 * price · its line over the last 24 hours); the bigger the widget, the more tiles (the owner 21-11: «ب سوي وكلما اكبر يسع اكثر … وخلي
 * شكل العملة بداخله · اخر ٢٤ ساعه بس خلي السعر يتحدث»).
 * It shares the first widget's fetch, cache and refresh: HolyWidget.tick (the watcher, every minute · KeepJob · the app) fetches
 * /api/app/widget when either widget is on the home screen, and HolyWidget.draw hands the same answer to draw() here.
 * Display only: no keys, no balances, no orders.
 */
public final class HolyPxWidget extends AppWidgetProvider {
    private static final int LAYOUT = 0x7f050000;      // the first widget's layout (one picture)
    private static final int IMG = 0x1020006;

    static int count(Context ctx) {
        try {
            int[] ids = AppWidgetManager.getInstance(ctx).getAppWidgetIds(new ComponentName(ctx, HolyPxWidget.class));
            return ids == null ? 0 : ids.length;
        } catch (Exception e) {
            return 0;
        }
    }

    static boolean any(Context ctx) {
        return count(ctx) > 0;
    }

    /** «📌 أضفه» from the page (Android 8+ and a launcher that allows it) — Android's own «add widget» sheet */
    static boolean pin(Context ctx) {
        try {
            AppWidgetManager am = AppWidgetManager.getInstance(ctx);
            Object ok = AppWidgetManager.class.getMethod("isRequestPinAppWidgetSupported").invoke(am);
            if (!Boolean.TRUE.equals(ok)) return false;
            Object r = AppWidgetManager.class.getMethod("requestPinAppWidget", ComponentName.class, Bundle.class, PendingIntent.class)
                    .invoke(am, new ComponentName(ctx, HolyPxWidget.class), null, null);
            return Boolean.TRUE.equals(r);
        } catch (Exception e) {
            return false;
        }
    }

    static void draw(Context ctx, String json, long ts) {
        try {
            AppWidgetManager am = AppWidgetManager.getInstance(ctx);
            int[] ids = am.getAppWidgetIds(new ComponentName(ctx, HolyPxWidget.class));
            if (ids == null || ids.length == 0) return;
            JSONObject j = null;
            if (json != null && !json.isEmpty()) {
                try {
                    j = new JSONObject(json);
                } catch (Exception e) {
                    j = null;
                }
            }
            Intent open = new Intent();
            open.setClassName(ctx, "com.holy.dash.MainActivity");
            open.setFlags(0x14000000);                  // NEW_TASK | RESET_TASK_IF_NEEDED (as the first widget)
            PendingIntent pi = PendingIntent.getActivity(ctx, 0x4850, open, 0x0c000000);      // IMMUTABLE | UPDATE_CURRENT
            float d = ctx.getResources().getDisplayMetrics().density;
            for (int id : ids) {
                Bundle o = am.getAppWidgetOptions(id);
                int w = o == null ? 0 : o.getInt("appWidgetMinWidth", 0);
                int h = o == null ? 0 : o.getInt("appWidgetMaxHeight", 0);
                if (w < 120) w = 320;
                if (h < 60) h = 180;
                RemoteViews rv = new RemoteViews(ctx.getPackageName(), LAYOUT);
                rv.setImageViewBitmap(IMG, WidgetArt.renderPx(ctx, j, ts, w, h, d));
                rv.setContentDescription(IMG, WidgetArt.speakPx(j));
                rv.setOnClickPendingIntent(IMG, pi);
                am.updateAppWidget(id, rv);
            }
        } catch (Exception e) {
            // a widget that cannot draw leaves its last picture
        }
    }

    private static void redraw(Context ctx) {
        SharedPreferences s = ctx.getSharedPreferences("holy_widget", 0);
        draw(ctx, s.getString("json", ""), s.getLong("ts", 0L));
    }

    /** the first widget's own refresh: fetch → cache → both widgets drawn */
    private static void refresh(Context ctx) {
        Intent i = new Intent("com.holy.dash.WIDGET_REFRESH");
        i.setClassName(ctx, "com.holy.dash.HolyWidget");
        ctx.sendBroadcast(i);
    }

    @Override
    public void onUpdate(Context ctx, AppWidgetManager am, int[] ids) {
        redraw(ctx);
        refresh(ctx);
    }

    @Override
    public void onAppWidgetOptionsChanged(Context ctx, AppWidgetManager am, int id, Bundle b) {
        redraw(ctx);
    }
}
