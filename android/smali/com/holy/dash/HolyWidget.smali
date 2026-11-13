.class public final Lcom/holy/dash/HolyWidget;
.super Landroid/appwidget/AppWidgetProvider;
.source "HolyWidget.java"


# static fields
.field static final ACT:Ljava/lang/String; = "com.holy.dash.WIDGET_REFRESH"

.field private static final BG:I = -0xdefefec

.field private static final DN:I = -0x10bab6

.field private static final LINE:I = 0x24ffffff

.field private static final MUT:I = -0x73736a

.field private static final TX:I = -0x1

.field private static final UP:I = -0xda58b0

.field private static volatile lastTick:J


# direct methods
.method static constructor <clinit>()V
    .registers 2

    .prologue
    .line 36
    const-wide/16 v0, 0x0

    sput-wide v0, Lcom/holy/dash/HolyWidget;->lastTick:J

    return-void
.end method

.method public constructor <init>()V
    .registers 1

    .prologue
    .line 34
    invoke-direct {p0}, Landroid/appwidget/AppWidgetProvider;-><init>()V

    return-void
.end method

.method static any(Landroid/content/Context;)Z
    .registers 2

    .prologue
    .line 67
    invoke-static {p0}, Lcom/holy/dash/HolyWidget;->count(Landroid/content/Context;)I

    move-result v0

    if-lez v0, :cond_8

    const/4 v0, 0x1

    :goto_7
    return v0

    :cond_8
    const/4 v0, 0x0

    goto :goto_7
.end method

.method static canPin(Landroid/content/Context;)Z
    .registers 4

    .prologue
    const/4 v1, 0x0

    .line 72
    sget v0, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v2, 0x1a

    if-ge v0, v2, :cond_8

    .line 77
    :goto_7
    return v1

    .line 74
    :cond_8
    :try_start_8
    const-class v0, Landroid/appwidget/AppWidgetManager;

    invoke-virtual {p0, v0}, Landroid/content/Context;->getSystemService(Ljava/lang/Class;)Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Landroid/appwidget/AppWidgetManager;

    .line 75
    if-eqz v0, :cond_1b

    invoke-virtual {v0}, Landroid/appwidget/AppWidgetManager;->isRequestPinAppWidgetSupported()Z
    :try_end_15
    .catch Ljava/lang/Exception; {:try_start_8 .. :try_end_15} :catch_1d

    move-result v0

    if-eqz v0, :cond_1b

    const/4 v0, 0x1

    :goto_19
    move v1, v0

    goto :goto_7

    :cond_1b
    move v0, v1

    goto :goto_19

    .line 76
    :catch_1d
    move-exception v0

    goto :goto_7
.end method

.method private static col(Ljava/lang/String;)I
    .registers 2

    .prologue
    .line 176
    const-string v0, "u"

    invoke-virtual {v0, p0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_c

    const v0, -0xda58b0

    :goto_b
    return v0

    :cond_c
    const-string v0, "d"

    invoke-virtual {v0, p0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_18

    const v0, -0x10bab6

    goto :goto_b

    :cond_18
    const/4 v0, -0x1

    goto :goto_b
.end method

.method static count(Landroid/content/Context;)I
    .registers 4

    .prologue
    .line 60
    :try_start_0
    invoke-static {p0}, Landroid/appwidget/AppWidgetManager;->getInstance(Landroid/content/Context;)Landroid/appwidget/AppWidgetManager;

    move-result-object v0

    new-instance v1, Landroid/content/ComponentName;

    const-class v2, Lcom/holy/dash/HolyWidget;

    invoke-direct {v1, p0, v2}, Landroid/content/ComponentName;-><init>(Landroid/content/Context;Ljava/lang/Class;)V

    invoke-virtual {v0, v1}, Landroid/appwidget/AppWidgetManager;->getAppWidgetIds(Landroid/content/ComponentName;)[I

    move-result-object v0

    array-length v0, v0
    :try_end_10
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_10} :catch_11

    .line 62
    :goto_10
    return v0

    .line 61
    :catch_11
    move-exception v0

    .line 62
    const/4 v0, 0x0

    goto :goto_10
.end method

.method static draw(Landroid/content/Context;Ljava/lang/String;J)V
    .registers 22

    .prologue
    .line 130
    :try_start_0
    invoke-static/range {p0 .. p0}, Landroid/appwidget/AppWidgetManager;->getInstance(Landroid/content/Context;)Landroid/appwidget/AppWidgetManager;

    move-result-object v10

    .line 131
    new-instance v2, Landroid/content/ComponentName;

    const-class v3, Lcom/holy/dash/HolyWidget;

    move-object/from16 v0, p0

    invoke-direct {v2, v0, v3}, Landroid/content/ComponentName;-><init>(Landroid/content/Context;Ljava/lang/Class;)V

    invoke-virtual {v10, v2}, Landroid/appwidget/AppWidgetManager;->getAppWidgetIds(Landroid/content/ComponentName;)[I

    move-result-object v11

    .line 132
    array-length v2, v11
    :try_end_12
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_12} :catch_aa

    if-nez v2, :cond_15

    .line 158
    :cond_14
    :goto_14
    return-void

    .line 133
    :cond_15
    const/4 v2, 0x0

    .line 135
    if-eqz p1, :cond_25

    :try_start_18
    invoke-virtual/range {p1 .. p1}, Ljava/lang/String;->isEmpty()Z

    move-result v3

    if-nez v3, :cond_25

    new-instance v2, Lorg/json/JSONObject;

    move-object/from16 v0, p1

    invoke-direct {v2, v0}, Lorg/json/JSONObject;-><init>(Ljava/lang/String;)V
    :try_end_25
    .catch Ljava/lang/Exception; {:try_start_18 .. :try_end_25} :catch_97

    :cond_25
    move-object v3, v2

    .line 139
    :goto_26
    :try_start_26
    new-instance v2, Landroid/content/Intent;

    const-class v4, Lcom/holy/dash/MainActivity;

    move-object/from16 v0, p0

    invoke-direct {v2, v0, v4}, Landroid/content/Intent;-><init>(Landroid/content/Context;Ljava/lang/Class;)V

    .line 140
    const/high16 v4, 0x14000000

    invoke-virtual {v2, v4}, Landroid/content/Intent;->setFlags(I)Landroid/content/Intent;

    .line 141
    const/16 v4, 0x484f

    const/high16 v5, 0xc000000

    move-object/from16 v0, p0

    invoke-static {v0, v4, v2, v5}, Landroid/app/PendingIntent;->getActivity(Landroid/content/Context;ILandroid/content/Intent;I)Landroid/app/PendingIntent;

    move-result-object v12

    .line 142
    invoke-virtual/range {p0 .. p0}, Landroid/content/Context;->getResources()Landroid/content/res/Resources;

    move-result-object v2

    invoke-virtual {v2}, Landroid/content/res/Resources;->getDisplayMetrics()Landroid/util/DisplayMetrics;

    move-result-object v2

    iget v8, v2, Landroid/util/DisplayMetrics;->density:F

    .line 143
    array-length v13, v11

    const/4 v2, 0x0

    move v9, v2

    :goto_4b
    if-ge v9, v13, :cond_14

    aget v14, v11, v9

    .line 144
    invoke-virtual {v10, v14}, Landroid/appwidget/AppWidgetManager;->getAppWidgetOptions(I)Landroid/os/Bundle;

    move-result-object v2

    .line 145
    if-nez v2, :cond_9a

    const/4 v6, 0x0

    .line 146
    :goto_56
    if-nez v2, :cond_a2

    const/4 v7, 0x0

    .line 147
    :goto_59
    const/16 v2, 0xa0

    if-ge v6, v2, :cond_5f

    const/16 v6, 0x140

    .line 148
    :cond_5f
    const/16 v2, 0x5a

    if-ge v7, v2, :cond_65

    const/16 v7, 0xb4

    .line 149
    :cond_65
    new-instance v15, Landroid/widget/RemoteViews;

    invoke-virtual/range {p0 .. p0}, Landroid/content/Context;->getPackageName()Ljava/lang/String;

    move-result-object v2

    const/high16 v4, 0x7f050000

    invoke-direct {v15, v2, v4}, Landroid/widget/RemoteViews;-><init>(Ljava/lang/String;I)V

    .line 150
    const v16, 0x1020006

    move-object/from16 v2, p0

    move-wide/from16 v4, p2

    invoke-static/range {v2 .. v8}, Lcom/holy/dash/HolyWidget;->render(Landroid/content/Context;Lorg/json/JSONObject;JIIF)Landroid/graphics/Bitmap;

    move-result-object v2

    move/from16 v0, v16

    invoke-virtual {v15, v0, v2}, Landroid/widget/RemoteViews;->setImageViewBitmap(ILandroid/graphics/Bitmap;)V

    .line 151
    const v2, 0x1020006

    invoke-static {v3}, Lcom/holy/dash/HolyWidget;->speak(Lorg/json/JSONObject;)Ljava/lang/String;

    move-result-object v4

    invoke-virtual {v15, v2, v4}, Landroid/widget/RemoteViews;->setContentDescription(ILjava/lang/CharSequence;)V

    .line 152
    const v2, 0x1020006

    invoke-virtual {v15, v2, v12}, Landroid/widget/RemoteViews;->setOnClickPendingIntent(ILandroid/app/PendingIntent;)V

    .line 153
    invoke-virtual {v10, v14, v15}, Landroid/appwidget/AppWidgetManager;->updateAppWidget(ILandroid/widget/RemoteViews;)V

    .line 143
    add-int/lit8 v2, v9, 0x1

    move v9, v2

    goto :goto_4b

    .line 136
    :catch_97
    move-exception v2

    .line 137
    const/4 v3, 0x0

    goto :goto_26

    .line 145
    :cond_9a
    const-string v4, "appWidgetMinWidth"

    const/4 v5, 0x0

    invoke-virtual {v2, v4, v5}, Landroid/os/Bundle;->getInt(Ljava/lang/String;I)I

    move-result v6

    goto :goto_56

    .line 146
    :cond_a2
    const-string v4, "appWidgetMaxHeight"

    const/4 v5, 0x0

    invoke-virtual {v2, v4, v5}, Landroid/os/Bundle;->getInt(Ljava/lang/String;I)I
    :try_end_a8
    .catch Ljava/lang/Exception; {:try_start_26 .. :try_end_a8} :catch_aa

    move-result v7

    goto :goto_59

    .line 155
    :catch_aa
    move-exception v2

    goto/16 :goto_14
.end method

.method static fetch(Landroid/content/Context;)V
    .registers 9

    .prologue
    const-wide/16 v6, 0x0

    .line 110
    invoke-static {p0}, Lcom/holy/dash/HolyWidget;->store(Landroid/content/Context;)Landroid/content/SharedPreferences;

    move-result-object v0

    .line 111
    invoke-static {p0}, Lcom/holy/dash/Prefs;->origin(Landroid/content/Context;)Ljava/lang/String;

    move-result-object v1

    invoke-static {p0}, Lcom/holy/dash/Prefs;->token(Landroid/content/Context;)Ljava/lang/String;

    move-result-object v2

    .line 112
    invoke-virtual {v1}, Ljava/lang/String;->isEmpty()Z

    move-result v3

    if-nez v3, :cond_95

    invoke-virtual {v2}, Ljava/lang/String;->isEmpty()Z

    move-result v3

    if-nez v3, :cond_95

    .line 114
    :try_start_1a
    new-instance v3, Ljava/util/HashMap;

    invoke-direct {v3}, Ljava/util/HashMap;-><init>()V

    .line 115
    const-string v4, "X-Holy-Device"

    invoke-interface {v3, v4, v2}, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;

    .line 116
    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v2, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v2, "/api/app/widget"

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    const/16 v2, 0x3a98

    const/4 v4, 0x1

    new-array v4, v4, [Ljava/net/HttpURLConnection;

    invoke-static {v1, v3, v2, v4}, Lcom/holy/dash/Net;->get(Ljava/lang/String;Ljava/util/Map;I[Ljava/net/HttpURLConnection;)Lcom/holy/dash/Net$Resp;

    move-result-object v1

    .line 117
    iget v2, v1, Lcom/holy/dash/Net$Resp;->code:I

    const/16 v3, 0xc8

    if-ne v2, v3, :cond_71

    invoke-interface {v0}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;

    move-result-object v2

    const-string v3, "json"

    iget-object v1, v1, Lcom/holy/dash/Net$Resp;->body:Ljava/lang/String;

    invoke-interface {v2, v3, v1}, Landroid/content/SharedPreferences$Editor;->putString(Ljava/lang/String;Ljava/lang/String;)Landroid/content/SharedPreferences$Editor;

    move-result-object v1

    const-string v2, "ts"

    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v4

    invoke-interface {v1, v2, v4, v5}, Landroid/content/SharedPreferences$Editor;->putLong(Ljava/lang/String;J)Landroid/content/SharedPreferences$Editor;

    move-result-object v1

    invoke-interface {v1}, Landroid/content/SharedPreferences$Editor;->apply()V
    :try_end_5f
    .catch Ljava/lang/Exception; {:try_start_1a .. :try_end_5f} :catch_93

    .line 125
    :cond_5f
    :goto_5f
    const-string v1, "json"

    const-string v2, ""

    invoke-interface {v0, v1, v2}, Landroid/content/SharedPreferences;->getString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    const-string v2, "ts"

    invoke-interface {v0, v2, v6, v7}, Landroid/content/SharedPreferences;->getLong(Ljava/lang/String;J)J

    move-result-wide v2

    invoke-static {p0, v1, v2, v3}, Lcom/holy/dash/HolyWidget;->draw(Landroid/content/Context;Ljava/lang/String;J)V

    .line 126
    return-void

    .line 118
    :cond_71
    :try_start_71
    iget v2, v1, Lcom/holy/dash/Net$Resp;->code:I

    const/16 v3, 0x191

    if-eq v2, v3, :cond_7d

    iget v1, v1, Lcom/holy/dash/Net$Resp;->code:I

    const/16 v2, 0x193

    if-ne v1, v2, :cond_5f

    :cond_7d
    invoke-interface {v0}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;

    move-result-object v1

    const-string v2, "json"

    invoke-interface {v1, v2}, Landroid/content/SharedPreferences$Editor;->remove(Ljava/lang/String;)Landroid/content/SharedPreferences$Editor;

    move-result-object v1

    const-string v2, "ts"

    const-wide/16 v4, 0x0

    invoke-interface {v1, v2, v4, v5}, Landroid/content/SharedPreferences$Editor;->putLong(Ljava/lang/String;J)Landroid/content/SharedPreferences$Editor;

    move-result-object v1

    invoke-interface {v1}, Landroid/content/SharedPreferences$Editor;->apply()V
    :try_end_92
    .catch Ljava/lang/Exception; {:try_start_71 .. :try_end_92} :catch_93

    goto :goto_5f

    .line 119
    :catch_93
    move-exception v1

    goto :goto_5f

    .line 123
    :cond_95
    invoke-interface {v0}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;

    move-result-object v1

    const-string v2, "json"

    invoke-interface {v1, v2}, Landroid/content/SharedPreferences$Editor;->remove(Ljava/lang/String;)Landroid/content/SharedPreferences$Editor;

    move-result-object v1

    const-string v2, "ts"

    invoke-interface {v1, v2, v6, v7}, Landroid/content/SharedPreferences$Editor;->putLong(Ljava/lang/String;J)Landroid/content/SharedPreferences$Editor;

    move-result-object v1

    invoke-interface {v1}, Landroid/content/SharedPreferences$Editor;->apply()V

    goto :goto_5f
.end method

.method private static paint(FIZLandroid/graphics/Paint$Align;)Landroid/graphics/Paint;
    .registers 6

    .prologue
    .line 180
    new-instance v1, Landroid/graphics/Paint;

    const/16 v0, 0x81

    invoke-direct {v1, v0}, Landroid/graphics/Paint;-><init>(I)V

    .line 181
    invoke-virtual {v1, p0}, Landroid/graphics/Paint;->setTextSize(F)V

    .line 182
    invoke-virtual {v1, p1}, Landroid/graphics/Paint;->setColor(I)V

    .line 183
    if-eqz p2, :cond_18

    sget-object v0, Landroid/graphics/Typeface;->DEFAULT_BOLD:Landroid/graphics/Typeface;

    :goto_11
    invoke-virtual {v1, v0}, Landroid/graphics/Paint;->setTypeface(Landroid/graphics/Typeface;)Landroid/graphics/Typeface;

    .line 184
    invoke-virtual {v1, p3}, Landroid/graphics/Paint;->setTextAlign(Landroid/graphics/Paint$Align;)V

    .line 185
    return-object v1

    .line 183
    :cond_18
    sget-object v0, Landroid/graphics/Typeface;->DEFAULT:Landroid/graphics/Typeface;

    goto :goto_11
.end method

.method static pin(Landroid/content/Context;)Z
    .registers 6

    .prologue
    const/4 v1, 0x0

    .line 82
    invoke-static {p0}, Lcom/holy/dash/HolyWidget;->canPin(Landroid/content/Context;)Z

    move-result v0

    if-nez v0, :cond_9

    move v0, v1

    .line 86
    :goto_8
    return v0

    .line 84
    :cond_9
    :try_start_9
    const-class v0, Landroid/appwidget/AppWidgetManager;

    invoke-virtual {p0, v0}, Landroid/content/Context;->getSystemService(Ljava/lang/Class;)Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Landroid/appwidget/AppWidgetManager;

    new-instance v2, Landroid/content/ComponentName;

    const-class v3, Lcom/holy/dash/HolyWidget;

    invoke-direct {v2, p0, v3}, Landroid/content/ComponentName;-><init>(Landroid/content/Context;Ljava/lang/Class;)V

    const/4 v3, 0x0

    const/4 v4, 0x0

    invoke-virtual {v0, v2, v3, v4}, Landroid/appwidget/AppWidgetManager;->requestPinAppWidget(Landroid/content/ComponentName;Landroid/os/Bundle;Landroid/app/PendingIntent;)Z
    :try_end_1d
    .catch Ljava/lang/Exception; {:try_start_9 .. :try_end_1d} :catch_1f

    move-result v0

    goto :goto_8

    .line 85
    :catch_1f
    move-exception v0

    move v0, v1

    .line 86
    goto :goto_8
.end method

.method static refreshAsync(Landroid/content/Context;)V
    .registers 4

    .prologue
    .line 99
    invoke-virtual {p0}, Landroid/content/Context;->getApplicationContext()Landroid/content/Context;

    move-result-object v0

    .line 100
    invoke-static {v0}, Lcom/holy/dash/HolyWidget;->any(Landroid/content/Context;)Z

    move-result v1

    if-nez v1, :cond_b

    .line 107
    :goto_a
    return-void

    .line 101
    :cond_b
    new-instance v1, Ljava/lang/Thread;

    new-instance v2, Lcom/holy/dash/HolyWidget$1;

    invoke-direct {v2, v0}, Lcom/holy/dash/HolyWidget$1;-><init>(Landroid/content/Context;)V

    const-string v0, "holy-widget"

    invoke-direct {v1, v2, v0}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;Ljava/lang/String;)V

    .line 106
    invoke-virtual {v1}, Ljava/lang/Thread;->start()V

    goto :goto_a
.end method

.method static render(Landroid/content/Context;Lorg/json/JSONObject;JIIF)Landroid/graphics/Bitmap;
    .registers 31

    .prologue
    .line 200
    const/4 v2, 0x1

    move/from16 v0, p4

    int-to-float v3, v0

    mul-float v3, v3, p6

    invoke-static {v3}, Ljava/lang/Math;->round(F)I

    move-result v3

    const/16 v4, 0x578

    invoke-static {v3, v4}, Ljava/lang/Math;->min(II)I

    move-result v3

    invoke-static {v2, v3}, Ljava/lang/Math;->max(II)I

    move-result v15

    const/4 v2, 0x1

    move/from16 v0, p5

    int-to-float v3, v0

    mul-float v3, v3, p6

    invoke-static {v3}, Ljava/lang/Math;->round(F)I

    move-result v3

    const/16 v4, 0x44c

    invoke-static {v3, v4}, Ljava/lang/Math;->min(II)I

    move-result v3

    invoke-static {v2, v3}, Ljava/lang/Math;->max(II)I

    move-result v14

    .line 201
    sget-object v2, Landroid/graphics/Bitmap$Config;->ARGB_8888:Landroid/graphics/Bitmap$Config;

    invoke-static {v15, v14, v2}, Landroid/graphics/Bitmap;->createBitmap(IILandroid/graphics/Bitmap$Config;)Landroid/graphics/Bitmap;

    move-result-object v13

    .line 202
    new-instance v2, Landroid/graphics/Canvas;

    invoke-direct {v2, v13}, Landroid/graphics/Canvas;-><init>(Landroid/graphics/Bitmap;)V

    .line 203
    new-instance v3, Landroid/graphics/Paint;

    const/4 v4, 0x1

    invoke-direct {v3, v4}, Landroid/graphics/Paint;-><init>(I)V

    .line 204
    const v4, -0xdefefec

    invoke-virtual {v3, v4}, Landroid/graphics/Paint;->setColor(I)V

    .line 205
    const/high16 v4, 0x41a00000    # 20.0f

    mul-float v4, v4, p6

    const/high16 v5, 0x41600000    # 14.0f

    mul-float v16, v5, p6

    .line 206
    new-instance v5, Landroid/graphics/RectF;

    const/4 v6, 0x0

    const/4 v7, 0x0

    int-to-float v8, v15

    int-to-float v9, v14

    invoke-direct {v5, v6, v7, v8, v9}, Landroid/graphics/RectF;-><init>(FFFF)V

    invoke-virtual {v2, v5, v4, v4, v3}, Landroid/graphics/Canvas;->drawRoundRect(Landroid/graphics/RectF;FFLandroid/graphics/Paint;)V

    .line 207
    new-instance v17, Landroid/graphics/Paint;

    const/4 v3, 0x1

    move-object/from16 v0, v17

    invoke-direct {v0, v3}, Landroid/graphics/Paint;-><init>(I)V

    .line 208
    sget-object v3, Landroid/graphics/Paint$Style;->STROKE:Landroid/graphics/Paint$Style;

    move-object/from16 v0, v17

    invoke-virtual {v0, v3}, Landroid/graphics/Paint;->setStyle(Landroid/graphics/Paint$Style;)V

    .line 209
    const/high16 v3, 0x3f800000    # 1.0f

    move/from16 v0, p6

    invoke-static {v3, v0}, Ljava/lang/Math;->max(FF)F

    move-result v3

    move-object/from16 v0, v17

    invoke-virtual {v0, v3}, Landroid/graphics/Paint;->setStrokeWidth(F)V

    .line 210
    const v3, 0x24ffffff

    move-object/from16 v0, v17

    invoke-virtual {v0, v3}, Landroid/graphics/Paint;->setColor(I)V

    .line 211
    new-instance v3, Landroid/graphics/RectF;

    const/high16 v5, 0x3f000000    # 0.5f

    const/high16 v6, 0x3f000000    # 0.5f

    int-to-float v7, v15

    const/high16 v8, 0x3f000000    # 0.5f

    sub-float/2addr v7, v8

    int-to-float v8, v14

    const/high16 v9, 0x3f000000    # 0.5f

    sub-float/2addr v8, v9

    invoke-direct {v3, v5, v6, v7, v8}, Landroid/graphics/RectF;-><init>(FFFF)V

    move-object/from16 v0, v17

    invoke-virtual {v2, v3, v4, v4, v0}, Landroid/graphics/Canvas;->drawRoundRect(Landroid/graphics/RectF;FFLandroid/graphics/Paint;)V

    .line 212
    int-to-float v3, v15

    sub-float v18, v3, v16

    const/high16 v3, 0x41600000    # 14.0f

    mul-float v3, v3, p6

    add-float v5, v16, v3

    .line 214
    const/high16 v3, 0x41800000    # 16.0f

    mul-float v3, v3, p6

    const/4 v4, -0x1

    const/4 v6, 0x1

    sget-object v7, Landroid/graphics/Paint$Align;->RIGHT:Landroid/graphics/Paint$Align;

    invoke-static {v3, v4, v6, v7}, Lcom/holy/dash/HolyWidget;->paint(FIZLandroid/graphics/Paint$Align;)Landroid/graphics/Paint;

    move-result-object v3

    .line 215
    const-string v4, "Holy"

    move/from16 v0, v18

    invoke-virtual {v2, v4, v0, v5, v3}, Landroid/graphics/Canvas;->drawText(Ljava/lang/String;FFLandroid/graphics/Paint;)V

    .line 216
    const-wide/16 v6, 0x0

    cmp-long v3, p2, v6

    if-lez v3, :cond_124

    new-instance v3, Ljava/text/SimpleDateFormat;

    const-string v4, "HH:mm"

    sget-object v6, Ljava/util/Locale;->US:Ljava/util/Locale;

    invoke-direct {v3, v4, v6}, Ljava/text/SimpleDateFormat;-><init>(Ljava/lang/String;Ljava/util/Locale;)V

    new-instance v4, Ljava/util/Date;

    move-wide/from16 v0, p2

    invoke-direct {v4, v0, v1}, Ljava/util/Date;-><init>(J)V

    invoke-virtual {v3, v4}, Ljava/text/SimpleDateFormat;->format(Ljava/util/Date;)Ljava/lang/String;

    move-result-object v3

    move-object v6, v3

    .line 217
    :goto_c4
    const-wide/16 v8, 0x0

    cmp-long v3, p2, v8

    if-lez v3, :cond_128

    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v8

    sub-long v8, v8, p2

    const-wide/32 v10, 0xdbba0

    cmp-long v3, v8, v10

    if-lez v3, :cond_128

    const/4 v3, 0x1

    move v4, v3

    .line 218
    :goto_d9
    if-nez p1, :cond_12b

    .line 219
    const/high16 v3, 0x41480000    # 12.5f

    mul-float v3, v3, p6

    const v4, -0x73736a

    const/4 v5, 0x0

    sget-object v6, Landroid/graphics/Paint$Align;->CENTER:Landroid/graphics/Paint$Align;

    invoke-static {v3, v4, v5, v6}, Lcom/holy/dash/HolyWidget;->paint(FIZLandroid/graphics/Paint$Align;)Landroid/graphics/Paint;

    move-result-object v7

    .line 220
    const-string v3, "\u0627\u0641\u062a\u062d Holy \u0648\u0627\u062f\u062e\u0644 \u0625\u0644\u0649 \u0644\u0648\u062d\u062a\u0643 \u0645\u0631\u0629 \u0648\u0627\u062d\u062f\u0629"

    int-to-float v4, v15

    const/high16 v5, 0x40000000    # 2.0f

    div-float/2addr v4, v5

    int-to-float v5, v14

    const/high16 v6, 0x40000000    # 2.0f

    div-float/2addr v5, v6

    int-to-float v6, v15

    const/high16 v8, 0x40000000    # 2.0f

    mul-float v8, v8, v16

    sub-float/2addr v6, v8

    invoke-static/range {v2 .. v7}, Lcom/holy/dash/HolyWidget;->text(Landroid/graphics/Canvas;Ljava/lang/String;FFFLandroid/graphics/Paint;)V

    .line 221
    const-string v3, "\u0644\u064a\u0631\u062a\u0628\u0637 \u0627\u0644\u062c\u0647\u0627\u0632 \u0648\u062a\u0638\u0647\u0631 \u0628\u0648\u062a\u0627\u062a\u0643 \u0648\u0623\u0631\u0628\u0627\u062d\u0643 \u0647\u0646\u0627"

    int-to-float v4, v15

    const/high16 v5, 0x40000000    # 2.0f

    div-float/2addr v4, v5

    int-to-float v5, v14

    const/high16 v6, 0x40000000    # 2.0f

    div-float/2addr v5, v6

    const/high16 v6, 0x41900000    # 18.0f

    mul-float v6, v6, p6

    add-float/2addr v5, v6

    int-to-float v6, v15

    const/high16 v7, 0x40000000    # 2.0f

    mul-float v7, v7, v16

    sub-float/2addr v6, v7

    const/high16 v7, 0x41300000    # 11.0f

    mul-float v7, v7, p6

    const v8, -0x73736a

    const/4 v9, 0x0

    sget-object v10, Landroid/graphics/Paint$Align;->CENTER:Landroid/graphics/Paint$Align;

    invoke-static {v7, v8, v9, v10}, Lcom/holy/dash/HolyWidget;->paint(FIZLandroid/graphics/Paint$Align;)Landroid/graphics/Paint;

    move-result-object v7

    invoke-static/range {v2 .. v7}, Lcom/holy/dash/HolyWidget;->text(Landroid/graphics/Canvas;Ljava/lang/String;FFFLandroid/graphics/Paint;)V

    move-object v2, v13

    .line 269
    :goto_123
    return-object v2

    .line 216
    :cond_124
    const-string v3, ""

    move-object v6, v3

    goto :goto_c4

    .line 217
    :cond_128
    const/4 v3, 0x0

    move v4, v3

    goto :goto_d9

    .line 224
    :cond_12b
    const-string v3, "run"

    const/4 v7, 0x0

    move-object/from16 v0, p1

    invoke-virtual {v0, v3, v7}, Lorg/json/JSONObject;->optInt(Ljava/lang/String;I)I

    move-result v7

    const-string v3, "n"

    const/4 v8, 0x0

    move-object/from16 v0, p1

    invoke-virtual {v0, v3, v8}, Lorg/json/JSONObject;->optInt(Ljava/lang/String;I)I

    move-result v8

    .line 225
    new-instance v9, Ljava/lang/StringBuilder;

    invoke-direct {v9}, Ljava/lang/StringBuilder;-><init>()V

    if-eqz v4, :cond_1c0

    const-string v3, "\u26a0\ufe0f "

    :goto_146
    invoke-virtual {v9, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    const-string v9, "\u25cf "

    invoke-virtual {v3, v9}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3, v7}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v3

    const-string v9, "/"

    invoke-virtual {v3, v9}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3, v8}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v3

    const-string v8, " \u064a\u0639\u0645\u0644"

    invoke-virtual {v3, v8}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v8

    invoke-virtual {v6}, Ljava/lang/String;->isEmpty()Z

    move-result v3

    if-eqz v3, :cond_1c3

    const-string v3, ""

    :goto_16c
    invoke-virtual {v8, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    .line 226
    const/high16 v6, 0x41300000    # 11.0f

    mul-float v6, v6, p6

    if-eqz v4, :cond_1d7

    const v4, -0x73736a

    :goto_17d
    const/4 v7, 0x0

    sget-object v8, Landroid/graphics/Paint$Align;->LEFT:Landroid/graphics/Paint$Align;

    invoke-static {v6, v4, v7, v8}, Lcom/holy/dash/HolyWidget;->paint(FIZLandroid/graphics/Paint$Align;)Landroid/graphics/Paint;

    move-result-object v7

    .line 227
    int-to-float v4, v15

    const v6, 0x3f0ccccd    # 0.55f

    mul-float/2addr v6, v4

    move/from16 v4, v16

    invoke-static/range {v2 .. v7}, Lcom/holy/dash/HolyWidget;->text(Landroid/graphics/Canvas;Ljava/lang/String;FFFLandroid/graphics/Paint;)V

    .line 229
    const-string v3, "k"

    move-object/from16 v0, p1

    invoke-virtual {v0, v3}, Lorg/json/JSONObject;->optJSONArray(Ljava/lang/String;)Lorg/json/JSONArray;

    move-result-object v19

    .line 230
    const/high16 v3, 0x41a00000    # 20.0f

    mul-float v3, v3, p6

    add-float/2addr v5, v3

    int-to-float v3, v15

    const/high16 v4, 0x40000000    # 2.0f

    mul-float v4, v4, v16

    sub-float/2addr v3, v4

    const/high16 v4, 0x40400000    # 3.0f

    div-float v20, v3, v4

    .line 231
    if-eqz v19, :cond_22d

    const/4 v3, 0x0

    move v12, v3

    :goto_1a9
    const/4 v3, 0x3

    invoke-virtual/range {v19 .. v19}, Lorg/json/JSONArray;->length()I

    move-result v4

    invoke-static {v3, v4}, Ljava/lang/Math;->min(II)I

    move-result v3

    if-ge v12, v3, :cond_22d

    .line 232
    move-object/from16 v0, v19

    invoke-virtual {v0, v12}, Lorg/json/JSONArray;->optJSONArray(I)Lorg/json/JSONArray;

    move-result-object v8

    .line 233
    if-nez v8, :cond_1e1

    .line 231
    :goto_1bc
    add-int/lit8 v3, v12, 0x1

    move v12, v3

    goto :goto_1a9

    .line 225
    :cond_1c0
    const-string v3, ""

    goto :goto_146

    :cond_1c3
    new-instance v3, Ljava/lang/StringBuilder;

    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V

    const-string v9, " \u00b7 "

    invoke-virtual {v3, v9}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    goto :goto_16c

    .line 226
    :cond_1d7
    if-lez v7, :cond_1dd

    const v4, -0xda58b0

    goto :goto_17d

    :cond_1dd
    const v4, -0x73736a

    goto :goto_17d

    .line 234
    :cond_1e1
    int-to-float v3, v12

    mul-float v3, v3, v20

    sub-float v4, v18, v3

    .line 235
    const/4 v3, 0x0

    invoke-virtual {v8, v3}, Lorg/json/JSONArray;->optString(I)Ljava/lang/String;

    move-result-object v3

    const/high16 v6, 0x40c00000    # 6.0f

    mul-float v6, v6, p6

    sub-float v6, v20, v6

    const/high16 v7, 0x41280000    # 10.5f

    mul-float v7, v7, p6

    const v9, -0x73736a

    const/4 v10, 0x0

    sget-object v11, Landroid/graphics/Paint$Align;->RIGHT:Landroid/graphics/Paint$Align;

    invoke-static {v7, v9, v10, v11}, Lcom/holy/dash/HolyWidget;->paint(FIZLandroid/graphics/Paint$Align;)Landroid/graphics/Paint;

    move-result-object v7

    invoke-static/range {v2 .. v7}, Lcom/holy/dash/HolyWidget;->text(Landroid/graphics/Canvas;Ljava/lang/String;FFFLandroid/graphics/Paint;)V

    .line 236
    const/4 v3, 0x1

    invoke-virtual {v8, v3}, Lorg/json/JSONArray;->optString(I)Ljava/lang/String;

    move-result-object v7

    const/high16 v3, 0x41980000    # 19.0f

    mul-float v3, v3, p6

    add-float v9, v5, v3

    const/high16 v3, 0x40c00000    # 6.0f

    mul-float v3, v3, p6

    sub-float v10, v20, v3

    const/high16 v3, 0x41800000    # 16.0f

    mul-float v3, v3, p6

    const/4 v6, 0x2

    invoke-virtual {v8, v6}, Lorg/json/JSONArray;->optString(I)Ljava/lang/String;

    move-result-object v6

    invoke-static {v6}, Lcom/holy/dash/HolyWidget;->col(Ljava/lang/String;)I

    move-result v6

    const/4 v8, 0x1

    sget-object v11, Landroid/graphics/Paint$Align;->RIGHT:Landroid/graphics/Paint$Align;

    invoke-static {v3, v6, v8, v11}, Lcom/holy/dash/HolyWidget;->paint(FIZLandroid/graphics/Paint$Align;)Landroid/graphics/Paint;

    move-result-object v11

    move-object v6, v2

    move v8, v4

    invoke-static/range {v6 .. v11}, Lcom/holy/dash/HolyWidget;->text(Landroid/graphics/Canvas;Ljava/lang/String;FFFLandroid/graphics/Paint;)V

    goto :goto_1bc

    .line 238
    :cond_22d
    const/high16 v3, 0x41f00000    # 30.0f

    mul-float v3, v3, p6

    add-float v4, v5, v3

    move/from16 v3, v16

    move/from16 v5, v18

    move v6, v4

    move-object/from16 v7, v17

    .line 239
    invoke-virtual/range {v2 .. v7}, Landroid/graphics/Canvas;->drawLine(FFFFLandroid/graphics/Paint;)V

    .line 241
    const-string v3, "bots"

    move-object/from16 v0, p1

    invoke-virtual {v0, v3}, Lorg/json/JSONObject;->optJSONArray(Ljava/lang/String;)Lorg/json/JSONArray;

    move-result-object v17

    .line 242
    const/high16 v3, 0x41a80000    # 21.0f

    mul-float v19, v3, p6

    const/high16 v3, 0x41880000    # 17.0f

    mul-float v3, v3, p6

    add-float v5, v4, v3

    .line 243
    int-to-float v3, v14

    sub-float v3, v3, v16

    const/high16 v4, 0x41500000    # 13.0f

    mul-float v4, v4, p6

    sub-float v4, v5, v4

    sub-float/2addr v3, v4

    div-float v3, v3, v19

    float-to-double v6, v3

    invoke-static {v6, v7}, Ljava/lang/Math;->floor(D)D

    move-result-wide v6

    double-to-int v4, v6

    .line 244
    if-nez v17, :cond_286

    const/4 v3, 0x0

    move v14, v3

    .line 245
    :goto_265
    if-nez v14, :cond_28c

    .line 246
    const-string v3, "\u0644\u0627 \u062a\u0648\u062c\u062f \u0628\u0648\u062a\u0627\u062a \u0628\u0639\u062f"

    int-to-float v4, v15

    const/high16 v6, 0x40000000    # 2.0f

    mul-float v6, v6, v16

    sub-float v6, v4, v6

    const/high16 v4, 0x41380000    # 11.5f

    mul-float v4, v4, p6

    const v7, -0x73736a

    const/4 v8, 0x0

    sget-object v9, Landroid/graphics/Paint$Align;->RIGHT:Landroid/graphics/Paint$Align;

    invoke-static {v4, v7, v8, v9}, Lcom/holy/dash/HolyWidget;->paint(FIZLandroid/graphics/Paint$Align;)Landroid/graphics/Paint;

    move-result-object v7

    move/from16 v4, v18

    invoke-static/range {v2 .. v7}, Lcom/holy/dash/HolyWidget;->text(Landroid/graphics/Canvas;Ljava/lang/String;FFFLandroid/graphics/Paint;)V

    move-object v2, v13

    .line 247
    goto/16 :goto_123

    .line 244
    :cond_286
    invoke-virtual/range {v17 .. v17}, Lorg/json/JSONArray;->length()I

    move-result v3

    move v14, v3

    goto :goto_265

    .line 249
    :cond_28c
    const/4 v3, 0x0

    invoke-static {v3, v4}, Ljava/lang/Math;->max(II)I

    move-result v3

    invoke-static {v14, v3}, Ljava/lang/Math;->min(II)I

    move-result v3

    .line 250
    if-ge v3, v14, :cond_29b

    if-lez v3, :cond_29b

    add-int/lit8 v3, v3, -0x1

    .line 251
    :cond_29b
    new-instance v20, Landroid/graphics/Paint;

    const/4 v4, 0x1

    move-object/from16 v0, v20

    invoke-direct {v0, v4}, Landroid/graphics/Paint;-><init>(I)V

    .line 252
    const/4 v4, 0x0

    move v12, v4

    :goto_2a5
    if-ge v12, v3, :cond_3a3

    .line 253
    move-object/from16 v0, v17

    invoke-virtual {v0, v12}, Lorg/json/JSONArray;->optJSONObject(I)Lorg/json/JSONObject;

    move-result-object v21

    .line 254
    if-nez v21, :cond_2b3

    .line 252
    :goto_2af
    add-int/lit8 v4, v12, 0x1

    move v12, v4

    goto :goto_2a5

    .line 255
    :cond_2b3
    int-to-float v4, v12

    mul-float v4, v4, v19

    add-float v9, v5, v4

    .line 256
    const-string v4, "on"

    const/4 v6, 0x0

    move-object/from16 v0, v21

    invoke-virtual {v0, v4, v6}, Lorg/json/JSONObject;->optInt(Ljava/lang/String;I)I

    move-result v4

    const/4 v6, 0x1

    if-ne v4, v6, :cond_39e

    const v4, -0xda58b0

    :goto_2c7
    move-object/from16 v0, v20

    invoke-virtual {v0, v4}, Landroid/graphics/Paint;->setColor(I)V

    .line 257
    const/high16 v4, 0x40400000    # 3.0f

    mul-float v4, v4, p6

    sub-float v4, v18, v4

    const/high16 v6, 0x40800000    # 4.0f

    mul-float v6, v6, p6

    sub-float v6, v9, v6

    const/high16 v7, 0x40400000    # 3.0f

    mul-float v7, v7, p6

    move-object/from16 v0, v20

    invoke-virtual {v2, v4, v6, v7, v0}, Landroid/graphics/Canvas;->drawCircle(FFFLandroid/graphics/Paint;)V

    .line 258
    new-instance v4, Ljava/lang/StringBuilder;

    invoke-direct {v4}, Ljava/lang/StringBuilder;-><init>()V

    const-string v6, "e"

    move-object/from16 v0, v21

    invoke-virtual {v0, v6}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v6

    invoke-virtual {v4, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    const-string v6, " "

    invoke-virtual {v4, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    const-string v6, "s"

    move-object/from16 v0, v21

    invoke-virtual {v0, v6}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v6

    invoke-virtual {v4, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    invoke-virtual {v4}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v7

    const/high16 v4, 0x41300000    # 11.0f

    mul-float v4, v4, p6

    sub-float v8, v18, v4

    int-to-float v4, v15

    const/high16 v6, 0x40000000    # 2.0f

    mul-float v6, v6, v16

    sub-float/2addr v4, v6

    const/high16 v6, 0x3f000000    # 0.5f

    mul-float v10, v4, v6

    const/high16 v4, 0x41480000    # 12.5f

    mul-float v4, v4, p6

    const/4 v6, -0x1

    const/4 v11, 0x1

    sget-object v22, Landroid/graphics/Paint$Align;->RIGHT:Landroid/graphics/Paint$Align;

    move-object/from16 v0, v22

    invoke-static {v4, v6, v11, v0}, Lcom/holy/dash/HolyWidget;->paint(FIZLandroid/graphics/Paint$Align;)Landroid/graphics/Paint;

    move-result-object v11

    move-object v6, v2

    invoke-static/range {v6 .. v11}, Lcom/holy/dash/HolyWidget;->text(Landroid/graphics/Canvas;Ljava/lang/String;FFFLandroid/graphics/Paint;)V

    .line 259
    const-string v4, "a"

    move-object/from16 v0, v21

    invoke-virtual {v0, v4}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v7

    const-string v4, "b"

    move-object/from16 v0, v21

    invoke-virtual {v0, v4}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v4

    .line 260
    const/high16 v6, 0x41380000    # 11.5f

    mul-float v6, v6, p6

    const-string v8, "c"

    move-object/from16 v0, v21

    invoke-virtual {v0, v8}, Lorg/json/JSONObject;->optString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v8

    invoke-static {v8}, Lcom/holy/dash/HolyWidget;->col(Ljava/lang/String;)I

    move-result v8

    const/4 v10, 0x1

    sget-object v11, Landroid/graphics/Paint$Align;->LEFT:Landroid/graphics/Paint$Align;

    invoke-static {v6, v8, v10, v11}, Lcom/holy/dash/HolyWidget;->paint(FIZLandroid/graphics/Paint$Align;)Landroid/graphics/Paint;

    move-result-object v11

    .line 261
    invoke-virtual {v11, v7}, Landroid/graphics/Paint;->measureText(Ljava/lang/String;)F

    move-result v6

    int-to-float v8, v15

    const/high16 v10, 0x40000000    # 2.0f

    mul-float v10, v10, v16

    sub-float/2addr v8, v10

    const v10, 0x3e75c28f    # 0.24f

    mul-float/2addr v8, v10

    invoke-static {v6, v8}, Ljava/lang/Math;->min(FF)F

    move-result v21

    .line 262
    int-to-float v6, v15

    const/high16 v8, 0x40000000    # 2.0f

    mul-float v8, v8, v16

    sub-float/2addr v6, v8

    const v8, 0x3e75c28f    # 0.24f

    mul-float v10, v6, v8

    move-object v6, v2

    move/from16 v8, v16

    invoke-static/range {v6 .. v11}, Lcom/holy/dash/HolyWidget;->text(Landroid/graphics/Canvas;Ljava/lang/String;FFFLandroid/graphics/Paint;)V

    .line 263
    add-float v6, v16, v21

    const/high16 v7, 0x41000000    # 8.0f

    mul-float v7, v7, p6

    add-float v8, v6, v7

    int-to-float v6, v15

    const/high16 v7, 0x40000000    # 2.0f

    mul-float v7, v7, v16

    sub-float/2addr v6, v7

    const v7, 0x3e6147ae    # 0.22f

    mul-float v10, v6, v7

    const/high16 v6, 0x41300000    # 11.0f

    mul-float v6, v6, p6

    const v7, -0x73736a

    const/4 v11, 0x0

    sget-object v21, Landroid/graphics/Paint$Align;->LEFT:Landroid/graphics/Paint$Align;

    move-object/from16 v0, v21

    invoke-static {v6, v7, v11, v0}, Lcom/holy/dash/HolyWidget;->paint(FIZLandroid/graphics/Paint$Align;)Landroid/graphics/Paint;

    move-result-object v11

    move-object v6, v2

    move-object v7, v4

    invoke-static/range {v6 .. v11}, Lcom/holy/dash/HolyWidget;->text(Landroid/graphics/Canvas;Ljava/lang/String;FFFLandroid/graphics/Paint;)V

    goto/16 :goto_2af

    .line 256
    :cond_39e
    const v4, -0x73736a

    goto/16 :goto_2c7

    .line 265
    :cond_3a3
    if-ge v3, v14, :cond_3de

    .line 266
    int-to-float v4, v3

    mul-float v4, v4, v19

    add-float/2addr v5, v4

    .line 267
    new-instance v4, Ljava/lang/StringBuilder;

    invoke-direct {v4}, Ljava/lang/StringBuilder;-><init>()V

    const-string v6, "\u0648"

    invoke-virtual {v4, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    sub-int v3, v14, v3

    invoke-virtual {v4, v3}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v3

    const-string v4, " \u0628\u0648\u062a\u0627\u062a \u0623\u062e\u0631\u0649 \u2014 \u0627\u0636\u063a\u0637 \u0644\u0644\u0641\u062a\u062d"

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    int-to-float v4, v15

    const/high16 v6, 0x40000000    # 2.0f

    mul-float v6, v6, v16

    sub-float v6, v4, v6

    const/high16 v4, 0x41280000    # 10.5f

    mul-float v4, v4, p6

    const v7, -0x73736a

    const/4 v8, 0x0

    sget-object v9, Landroid/graphics/Paint$Align;->RIGHT:Landroid/graphics/Paint$Align;

    invoke-static {v4, v7, v8, v9}, Lcom/holy/dash/HolyWidget;->paint(FIZLandroid/graphics/Paint$Align;)Landroid/graphics/Paint;

    move-result-object v7

    move/from16 v4, v18

    invoke-static/range {v2 .. v7}, Lcom/holy/dash/HolyWidget;->text(Landroid/graphics/Canvas;Ljava/lang/String;FFFLandroid/graphics/Paint;)V

    :cond_3de
    move-object v2, v13

    .line 269
    goto/16 :goto_123
.end method

.method static speak(Lorg/json/JSONObject;)Ljava/lang/String;
    .registers 8

    .prologue
    const/4 v1, 0x0

    .line 162
    if-nez p0, :cond_6

    const-string v0, "Holy \u2014 \u0627\u0641\u062a\u062d Holy \u0648\u0627\u062f\u062e\u0644 \u0625\u0644\u0649 \u0644\u0648\u062d\u062a\u0643 \u0645\u0631\u0629 \u0648\u0627\u062d\u062f\u0629"

    .line 169
    :goto_5
    return-object v0

    .line 163
    :cond_6
    new-instance v2, Ljava/lang/StringBuilder;

    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v3, "Holy \u2014 "

    invoke-virtual {v0, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v3, "run"

    invoke-virtual {p0, v3, v1}, Lorg/json/JSONObject;->optInt(Ljava/lang/String;I)I

    move-result v3

    invoke-virtual {v0, v3}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v3, "/"

    invoke-virtual {v0, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v3, "n"

    invoke-virtual {p0, v3, v1}, Lorg/json/JSONObject;->optInt(Ljava/lang/String;I)I

    move-result v3

    invoke-virtual {v0, v3}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v3, " \u064a\u0639\u0645\u0644"

    invoke-virtual {v0, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-direct {v2, v0}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    .line 164
    const-string v0, "k"

    invoke-virtual {p0, v0}, Lorg/json/JSONObject;->optJSONArray(Ljava/lang/String;)Lorg/json/JSONArray;

    move-result-object v3

    .line 165
    if-eqz v3, :cond_6e

    move v0, v1

    :goto_43
    invoke-virtual {v3}, Lorg/json/JSONArray;->length()I

    move-result v4

    if-ge v0, v4, :cond_6e

    .line 166
    invoke-virtual {v3, v0}, Lorg/json/JSONArray;->optJSONArray(I)Lorg/json/JSONArray;

    move-result-object v4

    .line 167
    if-eqz v4, :cond_6b

    const-string v5, " \u00b7 "

    invoke-virtual {v2, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v5

    invoke-virtual {v4, v1}, Lorg/json/JSONArray;->optString(I)Ljava/lang/String;

    move-result-object v6

    invoke-virtual {v5, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v5

    const-string v6, " "

    invoke-virtual {v5, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v5

    const/4 v6, 0x1

    invoke-virtual {v4, v6}, Lorg/json/JSONArray;->optString(I)Ljava/lang/String;

    move-result-object v4

    invoke-virtual {v5, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    .line 165
    :cond_6b
    add-int/lit8 v0, v0, 0x1

    goto :goto_43

    .line 169
    :cond_6e
    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    goto :goto_5
.end method

.method private static store(Landroid/content/Context;)Landroid/content/SharedPreferences;
    .registers 3

    .prologue
    .line 55
    const-string v0, "holy_widget"

    const/4 v1, 0x0

    invoke-virtual {p0, v0, v1}, Landroid/content/Context;->getSharedPreferences(Ljava/lang/String;I)Landroid/content/SharedPreferences;

    move-result-object v0

    return-object v0
.end method

.method private static text(Landroid/graphics/Canvas;Ljava/lang/String;FFFLandroid/graphics/Paint;)V
    .registers 8

    .prologue
    .line 190
    if-nez p1, :cond_4

    const-string p1, ""

    .line 191
    :cond_4
    invoke-virtual {p5}, Landroid/graphics/Paint;->getTextSize()F

    move-result v0

    .line 192
    :goto_8
    const/high16 v1, 0x40c00000    # 6.0f

    cmpl-float v1, v0, v1

    if-lez v1, :cond_1d

    invoke-virtual {p5, p1}, Landroid/graphics/Paint;->measureText(Ljava/lang/String;)F

    move-result v1

    cmpl-float v1, v1, p4

    if-lez v1, :cond_1d

    .line 193
    const/high16 v1, 0x3f000000    # 0.5f

    sub-float/2addr v0, v1

    .line 194
    invoke-virtual {p5, v0}, Landroid/graphics/Paint;->setTextSize(F)V

    goto :goto_8

    .line 196
    :cond_1d
    invoke-virtual {p0, p1, p2, p3, p5}, Landroid/graphics/Canvas;->drawText(Ljava/lang/String;FFLandroid/graphics/Paint;)V

    .line 197
    return-void
.end method

.method static tick(Landroid/content/Context;)V
    .registers 7

    .prologue
    .line 92
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v0

    .line 93
    sget-wide v2, Lcom/holy/dash/HolyWidget;->lastTick:J

    sub-long v2, v0, v2

    const-wide/32 v4, 0xea60

    cmp-long v2, v2, v4

    if-gez v2, :cond_10

    .line 96
    :cond_f
    :goto_f
    return-void

    .line 94
    :cond_10
    sput-wide v0, Lcom/holy/dash/HolyWidget;->lastTick:J

    .line 95
    invoke-static {p0}, Lcom/holy/dash/HolyWidget;->any(Landroid/content/Context;)Z

    move-result v0

    if-eqz v0, :cond_f

    invoke-static {p0}, Lcom/holy/dash/HolyWidget;->fetch(Landroid/content/Context;)V

    goto :goto_f
.end method


# virtual methods
.method public onAppWidgetOptionsChanged(Landroid/content/Context;Landroid/appwidget/AppWidgetManager;ILandroid/os/Bundle;)V
    .registers 11

    .prologue
    .line 45
    invoke-static {p1}, Lcom/holy/dash/HolyWidget;->store(Landroid/content/Context;)Landroid/content/SharedPreferences;

    move-result-object v0

    const-string v1, "json"

    const-string v2, ""

    invoke-interface {v0, v1, v2}, Landroid/content/SharedPreferences;->getString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    invoke-static {p1}, Lcom/holy/dash/HolyWidget;->store(Landroid/content/Context;)Landroid/content/SharedPreferences;

    move-result-object v1

    const-string v2, "ts"

    const-wide/16 v4, 0x0

    invoke-interface {v1, v2, v4, v5}, Landroid/content/SharedPreferences;->getLong(Ljava/lang/String;J)J

    move-result-wide v2

    invoke-static {p1, v0, v2, v3}, Lcom/holy/dash/HolyWidget;->draw(Landroid/content/Context;Ljava/lang/String;J)V

    .line 46
    return-void
.end method

.method public onReceive(Landroid/content/Context;Landroid/content/Intent;)V
    .registers 5

    .prologue
    .line 50
    invoke-super {p0, p1, p2}, Landroid/appwidget/AppWidgetProvider;->onReceive(Landroid/content/Context;Landroid/content/Intent;)V

    .line 51
    if-eqz p2, :cond_14

    const-string v0, "com.holy.dash.WIDGET_REFRESH"

    invoke-virtual {p2}, Landroid/content/Intent;->getAction()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_14

    invoke-static {p1}, Lcom/holy/dash/HolyWidget;->refreshAsync(Landroid/content/Context;)V

    .line 52
    :cond_14
    return-void
.end method

.method public onUpdate(Landroid/content/Context;Landroid/appwidget/AppWidgetManager;[I)V
    .registers 4

    .prologue
    .line 40
    invoke-static {p1}, Lcom/holy/dash/HolyWidget;->refreshAsync(Landroid/content/Context;)V

    .line 41
    return-void
.end method
