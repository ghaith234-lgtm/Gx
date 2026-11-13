.class final Lcom/holy/dash/Feed;
.super Ljava/lang/Object;
.source "Feed.java"


# static fields
.field static final FAIL:I = 0x2

.field static final OK:I = 0x0

.field static final UNPAIRED:I = 0x1


# direct methods
.method private constructor <init>()V
    .registers 1

    .prologue
    .line 17
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method static declared-synchronized handle(Landroid/content/Context;Lcom/holy/dash/Net$Resp;)I
    .registers 16

    .prologue
    .line 23
    const-class v5, Lcom/holy/dash/Feed;

    monitor-enter v5

    :try_start_3
    iget v0, p1, Lcom/holy/dash/Net$Resp;->code:I

    const/16 v1, 0x191

    if-eq v0, v1, :cond_f

    iget v0, p1, Lcom/holy/dash/Net$Resp;->code:I

    const/16 v1, 0x193

    if-ne v0, v1, :cond_18

    .line 24
    :cond_f
    invoke-static {p0}, Lcom/holy/dash/Prefs;->clearPair(Landroid/content/Context;)V

    .line 25
    invoke-static {p0}, Lcom/holy/dash/Notif;->unpaired(Landroid/content/Context;)V
    :try_end_15
    .catchall {:try_start_3 .. :try_end_15} :catchall_82

    .line 26
    const/4 v0, 0x1

    .line 51
    :goto_16
    monitor-exit v5

    return v0

    .line 28
    :cond_18
    :try_start_18
    iget v0, p1, Lcom/holy/dash/Net$Resp;->code:I
    :try_end_1a
    .catchall {:try_start_18 .. :try_end_1a} :catchall_82

    const/16 v1, 0xc8

    if-eq v0, v1, :cond_20

    const/4 v0, 0x2

    goto :goto_16

    .line 30
    :cond_20
    :try_start_20
    invoke-static {p0}, Lcom/holy/dash/Prefs;->lastId(Landroid/content/Context;)J

    move-result-wide v2

    .line 31
    new-instance v0, Lorg/json/JSONObject;

    iget-object v1, p1, Lcom/holy/dash/Net$Resp;->body:Ljava/lang/String;

    invoke-direct {v0, v1}, Lorg/json/JSONObject;-><init>(Ljava/lang/String;)V

    .line 32
    const-string v1, "last"

    invoke-virtual {v0, v1, v2, v3}, Lorg/json/JSONObject;->optLong(Ljava/lang/String;J)J

    move-result-wide v6

    .line 33
    const-string v1, "items"

    invoke-virtual {v0, v1}, Lorg/json/JSONObject;->optJSONArray(Ljava/lang/String;)Lorg/json/JSONArray;

    move-result-object v8

    .line 34
    cmp-long v0, v6, v2

    if-gez v0, :cond_47

    .line 35
    invoke-static {p0, v6, v7}, Lcom/holy/dash/Prefs;->setLastId(Landroid/content/Context;J)V

    .line 48
    :goto_3e
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v0

    invoke-static {p0, v0, v1}, Lcom/holy/dash/Prefs;->setLastPoll(Landroid/content/Context;J)V

    .line 49
    const/4 v0, 0x0

    goto :goto_16

    .line 37
    :cond_47
    new-instance v9, Lorg/json/JSONArray;

    invoke-direct {v9}, Lorg/json/JSONArray;-><init>()V

    .line 39
    if-eqz v8, :cond_73

    const/4 v4, 0x0

    move-wide v0, v2

    :goto_50
    invoke-virtual {v8}, Lorg/json/JSONArray;->length()I

    move-result v10

    if-ge v4, v10, :cond_74

    .line 40
    invoke-virtual {v8, v4}, Lorg/json/JSONArray;->optJSONObject(I)Lorg/json/JSONObject;

    move-result-object v10

    .line 41
    if-nez v10, :cond_5f

    .line 39
    :cond_5c
    :goto_5c
    add-int/lit8 v4, v4, 0x1

    goto :goto_50

    .line 42
    :cond_5f
    const-string v11, "id"

    const-wide/16 v12, 0x0

    invoke-virtual {v10, v11, v12, v13}, Lorg/json/JSONObject;->optLong(Ljava/lang/String;J)J

    move-result-wide v12

    .line 43
    cmp-long v11, v12, v2

    if-lez v11, :cond_5c

    invoke-virtual {v9, v10}, Lorg/json/JSONArray;->put(Ljava/lang/Object;)Lorg/json/JSONArray;

    invoke-static {v0, v1, v12, v13}, Ljava/lang/Math;->max(JJ)J

    move-result-wide v0

    goto :goto_5c

    :cond_73
    move-wide v0, v2

    .line 45
    :cond_74
    invoke-static {p0, v9}, Lcom/holy/dash/Notif;->show(Landroid/content/Context;Lorg/json/JSONArray;)V

    .line 46
    invoke-static {v0, v1, v6, v7}, Ljava/lang/Math;->max(JJ)J

    move-result-wide v0

    invoke-static {p0, v0, v1}, Lcom/holy/dash/Prefs;->setLastId(Landroid/content/Context;J)V
    :try_end_7e
    .catch Ljava/lang/Exception; {:try_start_20 .. :try_end_7e} :catch_7f
    .catchall {:try_start_20 .. :try_end_7e} :catchall_82

    goto :goto_3e

    .line 50
    :catch_7f
    move-exception v0

    .line 51
    const/4 v0, 0x2

    goto :goto_16

    .line 23
    :catchall_82
    move-exception v0

    monitor-exit v5

    throw v0
.end method

.method static pollOnce(Landroid/content/Context;)I
    .registers 7

    .prologue
    const/4 v0, 0x2

    .line 57
    invoke-static {p0}, Lcom/holy/dash/Prefs;->origin(Landroid/content/Context;)Ljava/lang/String;

    move-result-object v1

    invoke-static {p0}, Lcom/holy/dash/Prefs;->token(Landroid/content/Context;)Ljava/lang/String;

    move-result-object v2

    .line 58
    invoke-virtual {v1}, Ljava/lang/String;->isEmpty()Z

    move-result v3

    if-nez v3, :cond_1b

    invoke-virtual {v2}, Ljava/lang/String;->isEmpty()Z

    move-result v3

    if-nez v3, :cond_1b

    invoke-static {p0}, Lcom/holy/dash/Prefs;->watch(Landroid/content/Context;)Z

    move-result v3

    if-nez v3, :cond_1c

    .line 65
    :cond_1b
    :goto_1b
    return v0

    .line 60
    :cond_1c
    :try_start_1c
    new-instance v3, Ljava/util/HashMap;

    invoke-direct {v3}, Ljava/util/HashMap;-><init>()V

    .line 61
    const-string v4, "X-Holy-Device"

    invoke-interface {v3, v4, v2}, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;

    .line 62
    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v2, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v2, "/api/app/feed?since="

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-static {p0}, Lcom/holy/dash/Prefs;->lastId(Landroid/content/Context;)J

    move-result-wide v4

    invoke-virtual {v1, v4, v5}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v2, "&wait=0"

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    const/16 v2, 0x4e20

    const/4 v4, 0x1

    new-array v4, v4, [Ljava/net/HttpURLConnection;

    invoke-static {v1, v3, v2, v4}, Lcom/holy/dash/Net;->get(Ljava/lang/String;Ljava/util/Map;I[Ljava/net/HttpURLConnection;)Lcom/holy/dash/Net$Resp;

    move-result-object v1

    .line 63
    invoke-static {p0, v1}, Lcom/holy/dash/Feed;->handle(Landroid/content/Context;Lcom/holy/dash/Net$Resp;)I
    :try_end_53
    .catch Ljava/lang/Exception; {:try_start_1c .. :try_end_53} :catch_55

    move-result v0

    goto :goto_1b

    .line 64
    :catch_55
    move-exception v1

    goto :goto_1b
.end method
