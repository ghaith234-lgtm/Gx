.class final Lcom/holy/dash/MainActivity$Bridge;
.super Ljava/lang/Object;
.source "MainActivity.java"


# annotations
.annotation system Ldalvik/annotation/EnclosingClass;
    value = Lcom/holy/dash/MainActivity;
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x10
    name = "Bridge"
.end annotation


# instance fields
.field final synthetic this$0:Lcom/holy/dash/MainActivity;


# direct methods
.method constructor <init>(Lcom/holy/dash/MainActivity;)V
    .registers 2

    .prologue
    .line 1059
    iput-object p1, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public askBattery()V
    .registers 2
    .annotation runtime Landroid/webkit/JavascriptInterface;
    .end annotation

    .prologue
    .line 1141
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity$Bridge;->ok()Z

    move-result v0

    if-nez v0, :cond_7

    .line 1143
    :goto_6
    return-void

    .line 1142
    :cond_7
    new-instance v0, Lcom/holy/dash/MainActivity$Bridge$4;

    invoke-direct {v0, p0}, Lcom/holy/dash/MainActivity$Bridge$4;-><init>(Lcom/holy/dash/MainActivity$Bridge;)V

    invoke-virtual {p0, v0}, Lcom/holy/dash/MainActivity$Bridge;->onUi(Ljava/lang/Runnable;)V

    goto :goto_6
.end method

.method public askNotif()V
    .registers 2
    .annotation runtime Landroid/webkit/JavascriptInterface;
    .end annotation

    .prologue
    .line 1135
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity$Bridge;->ok()Z

    move-result v0

    if-nez v0, :cond_7

    .line 1137
    :goto_6
    return-void

    .line 1136
    :cond_7
    new-instance v0, Lcom/holy/dash/MainActivity$Bridge$3;

    invoke-direct {v0, p0}, Lcom/holy/dash/MainActivity$Bridge$3;-><init>(Lcom/holy/dash/MainActivity$Bridge;)V

    invoke-virtual {p0, v0}, Lcom/holy/dash/MainActivity$Bridge;->onUi(Ljava/lang/Runnable;)V

    goto :goto_6
.end method

.method public bgSettings()V
    .registers 2
    .annotation runtime Landroid/webkit/JavascriptInterface;
    .end annotation

    .prologue
    .line 1147
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity$Bridge;->ok()Z

    move-result v0

    if-nez v0, :cond_7

    .line 1149
    :goto_6
    return-void

    .line 1148
    :cond_7
    new-instance v0, Lcom/holy/dash/MainActivity$Bridge$5;

    invoke-direct {v0, p0}, Lcom/holy/dash/MainActivity$Bridge$5;-><init>(Lcom/holy/dash/MainActivity$Bridge;)V

    invoke-virtual {p0, v0}, Lcom/holy/dash/MainActivity$Bridge;->onUi(Ljava/lang/Runnable;)V

    goto :goto_6
.end method

.method public bioUnlock()Z
    .registers 2
    .annotation runtime Landroid/webkit/JavascriptInterface;
    .end annotation

    .prologue
    .line 1189
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity$Bridge;->ok()Z

    move-result v0

    if-eqz v0, :cond_22

    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-static {v0}, Lcom/holy/dash/Prefs;->lock(Landroid/content/Context;)Z

    move-result v0

    if-eqz v0, :cond_22

    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-static {v0}, Lcom/holy/dash/Prefs;->bio(Landroid/content/Context;)Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/String;->isEmpty()Z

    move-result v0

    if-nez v0, :cond_22

    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-static {v0}, Lcom/holy/dash/Prefs;->paired(Landroid/content/Context;)Z

    move-result v0

    if-nez v0, :cond_24

    :cond_22
    const/4 v0, 0x0

    .line 1199
    :goto_23
    return v0

    .line 1190
    :cond_24
    new-instance v0, Lcom/holy/dash/MainActivity$Bridge$8;

    invoke-direct {v0, p0}, Lcom/holy/dash/MainActivity$Bridge$8;-><init>(Lcom/holy/dash/MainActivity$Bridge;)V

    invoke-virtual {p0, v0}, Lcom/holy/dash/MainActivity$Bridge;->onUi(Ljava/lang/Runnable;)V

    .line 1199
    const/4 v0, 0x1

    goto :goto_23
.end method

.method public changeServer()V
    .registers 2
    .annotation runtime Landroid/webkit/JavascriptInterface;
    .end annotation

    .prologue
    .line 1229
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity$Bridge;->ok()Z

    move-result v0

    if-nez v0, :cond_7

    .line 1231
    :goto_6
    return-void

    .line 1230
    :cond_7
    new-instance v0, Lcom/holy/dash/MainActivity$Bridge$11;

    invoke-direct {v0, p0}, Lcom/holy/dash/MainActivity$Bridge$11;-><init>(Lcom/holy/dash/MainActivity$Bridge;)V

    invoke-virtual {p0, v0}, Lcom/holy/dash/MainActivity$Bridge;->onUi(Ljava/lang/Runnable;)V

    goto :goto_6
.end method

.method public checkUpdate()V
    .registers 2
    .annotation runtime Landroid/webkit/JavascriptInterface;
    .end annotation

    .prologue
    .line 1217
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity$Bridge;->ok()Z

    move-result v0

    if-nez v0, :cond_7

    .line 1219
    :goto_6
    return-void

    .line 1218
    :cond_7
    new-instance v0, Lcom/holy/dash/MainActivity$Bridge$10;

    invoke-direct {v0, p0}, Lcom/holy/dash/MainActivity$Bridge$10;-><init>(Lcom/holy/dash/MainActivity$Bridge;)V

    invoke-virtual {p0, v0}, Lcom/holy/dash/MainActivity$Bridge;->onUi(Ljava/lang/Runnable;)V

    goto :goto_6
.end method

.method public copy(Ljava/lang/String;)V
    .registers 4
    .annotation runtime Landroid/webkit/JavascriptInterface;
    .end annotation

    .prologue
    .line 1241
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity$Bridge;->ok()Z

    move-result v0

    if-eqz v0, :cond_11

    if-eqz p1, :cond_11

    invoke-virtual {p1}, Ljava/lang/String;->length()I

    move-result v0

    const v1, 0x30d40

    if-le v0, v1, :cond_12

    .line 1249
    :cond_11
    :goto_11
    return-void

    .line 1242
    :cond_12
    new-instance v0, Lcom/holy/dash/MainActivity$Bridge$13;

    invoke-direct {v0, p0, p1}, Lcom/holy/dash/MainActivity$Bridge$13;-><init>(Lcom/holy/dash/MainActivity$Bridge;Ljava/lang/String;)V

    invoke-virtual {p0, v0}, Lcom/holy/dash/MainActivity$Bridge;->onUi(Ljava/lang/Runnable;)V

    goto :goto_11
.end method

.method public forget()V
    .registers 2
    .annotation runtime Landroid/webkit/JavascriptInterface;
    .end annotation

    .prologue
    .line 1116
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity$Bridge;->ok()Z

    move-result v0

    if-nez v0, :cond_7

    .line 1119
    :goto_6
    return-void

    .line 1117
    :cond_7
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-static {v0}, Lcom/holy/dash/Prefs;->clearPair(Landroid/content/Context;)V

    .line 1118
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-static {v0}, Lcom/holy/dash/WatchService;->stop(Landroid/content/Context;)V

    goto :goto_6
.end method

.method public needPair()Z
    .registers 2
    .annotation runtime Landroid/webkit/JavascriptInterface;
    .end annotation

    .prologue
    .line 1087
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity$Bridge;->ok()Z

    move-result v0

    if-eqz v0, :cond_18

    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-static {v0}, Lcom/holy/dash/Prefs;->paired(Landroid/content/Context;)Z

    move-result v0

    if-nez v0, :cond_18

    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-static {v0}, Lcom/holy/dash/Prefs;->autoPairOk(Landroid/content/Context;)Z

    move-result v0

    if-eqz v0, :cond_18

    const/4 v0, 0x1

    :goto_17
    return v0

    :cond_18
    const/4 v0, 0x0

    goto :goto_17
.end method

.method ok()Z
    .registers 3

    .prologue
    .line 1061
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v0, v0, Lcom/holy/dash/MainActivity;->origin:Ljava/lang/String;

    invoke-virtual {v0}, Ljava/lang/String;->isEmpty()Z

    move-result v0

    if-nez v0, :cond_1a

    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v0, v0, Lcom/holy/dash/MainActivity;->origin:Ljava/lang/String;

    iget-object v1, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v1, v1, Lcom/holy/dash/MainActivity;->pageOrigin:Ljava/lang/String;

    invoke-virtual {v0, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_1a

    const/4 v0, 0x1

    :goto_19
    return v0

    :cond_1a
    const/4 v0, 0x0

    goto :goto_19
.end method

.method onUi(Ljava/lang/Runnable;)V
    .registers 3

    .prologue
    .line 1063
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v0, v0, Lcom/holy/dash/MainActivity;->ui:Landroid/os/Handler;

    invoke-virtual {v0, p1}, Landroid/os/Handler;->post(Ljava/lang/Runnable;)Z

    return-void
.end method

.method public pair(Ljava/lang/String;Ljava/lang/String;J)V
    .registers 10
    .annotation runtime Landroid/webkit/JavascriptInterface;
    .end annotation

    .prologue
    .line 1103
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity$Bridge;->ok()Z

    move-result v0

    if-eqz v0, :cond_18

    if-eqz p2, :cond_18

    invoke-virtual {p2}, Ljava/lang/String;->length()I

    move-result v0

    const/16 v1, 0x14

    if-lt v0, v1, :cond_18

    invoke-virtual {p2}, Ljava/lang/String;->length()I

    move-result v0

    const/16 v1, 0xc8

    if-le v0, v1, :cond_19

    .line 1112
    :cond_18
    :goto_18
    return-void

    .line 1104
    :cond_19
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    if-nez p1, :cond_1f

    const-string p1, ""

    :cond_1f
    const-wide/16 v2, 0x0

    invoke-static {v2, v3, p3, p4}, Ljava/lang/Math;->max(JJ)J

    move-result-wide v2

    invoke-static {v0, p1, p2, v2, v3}, Lcom/holy/dash/Prefs;->setPair(Landroid/content/Context;Ljava/lang/String;Ljava/lang/String;J)V

    .line 1105
    new-instance v0, Lcom/holy/dash/MainActivity$Bridge$1;

    invoke-direct {v0, p0}, Lcom/holy/dash/MainActivity$Bridge$1;-><init>(Lcom/holy/dash/MainActivity$Bridge;)V

    invoke-virtual {p0, v0}, Lcom/holy/dash/MainActivity$Bridge;->onUi(Ljava/lang/Runnable;)V

    goto :goto_18
.end method

.method public pairInfo()Ljava/lang/String;
    .registers 7
    .annotation runtime Landroid/webkit/JavascriptInterface;
    .end annotation

    .prologue
    .line 1091
    new-instance v0, Lorg/json/JSONObject;

    invoke-direct {v0}, Lorg/json/JSONObject;-><init>()V

    .line 1093
    :try_start_5
    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    sget-object v2, Landroid/os/Build;->MANUFACTURER:Ljava/lang/String;

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v2, " "

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    sget-object v2, Landroid/os/Build;->MODEL:Ljava/lang/String;

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/String;->trim()Ljava/lang/String;

    move-result-object v1

    .line 1094
    const-string v2, "name"

    const/4 v3, 0x0

    const/16 v4, 0x3c

    invoke-virtual {v1}, Ljava/lang/String;->length()I

    move-result v5

    invoke-static {v4, v5}, Ljava/lang/Math;->min(II)I

    move-result v4

    invoke-virtual {v1, v3, v4}, Ljava/lang/String;->substring(II)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v2, v1}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    move-result-object v1

    const-string v2, "iid"

    iget-object v3, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-static {v3}, Lcom/holy/dash/Prefs;->installId(Landroid/content/Context;)Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v1, v2, v3}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    move-result-object v1

    const-string v2, "code"

    const/16 v3, 0xd

    invoke-virtual {v1, v2, v3}, Lorg/json/JSONObject;->put(Ljava/lang/String;I)Lorg/json/JSONObject;
    :try_end_4c
    .catch Ljava/lang/Exception; {:try_start_5 .. :try_end_4c} :catch_51

    .line 1098
    :goto_4c
    invoke-virtual {v0}, Lorg/json/JSONObject;->toString()Ljava/lang/String;

    move-result-object v0

    return-object v0

    .line 1095
    :catch_51
    move-exception v1

    goto :goto_4c
.end method

.method public pinWidget()Z
    .registers 2
    .annotation runtime Landroid/webkit/JavascriptInterface;
    .end annotation

    .prologue
    .line 1224
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity$Bridge;->ok()Z

    move-result v0

    if-eqz v0, :cond_10

    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-static {v0}, Lcom/holy/dash/HolyWidget;->pin(Landroid/content/Context;)Z

    move-result v0

    if-eqz v0, :cond_10

    const/4 v0, 0x1

    :goto_f
    return v0

    :cond_10
    const/4 v0, 0x0

    goto :goto_f
.end method

.method public saveFile(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V
    .registers 8
    .annotation runtime Landroid/webkit/JavascriptInterface;
    .end annotation

    .prologue
    const/4 v3, 0x0

    .line 1253
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity$Bridge;->ok()Z

    move-result v0

    if-eqz v0, :cond_9

    if-nez p3, :cond_a

    .line 1269
    :cond_9
    :goto_9
    return-void

    .line 1254
    :cond_a
    invoke-static {p1}, Lcom/holy/dash/MainActivity;->safeName(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    .line 1255
    if-eqz p2, :cond_16

    invoke-virtual {p2}, Ljava/lang/String;->isEmpty()Z

    move-result v0

    if-eqz v0, :cond_25

    :cond_16
    const-string v0, "application/octet-stream"

    .line 1256
    :goto_18
    invoke-static {p3, v3}, Landroid/util/Base64;->decode(Ljava/lang/String;I)[B

    move-result-object v2

    .line 1257
    new-instance v3, Lcom/holy/dash/MainActivity$Bridge$14;

    invoke-direct {v3, p0, v2, v1, v0}, Lcom/holy/dash/MainActivity$Bridge$14;-><init>(Lcom/holy/dash/MainActivity$Bridge;[BLjava/lang/String;Ljava/lang/String;)V

    invoke-virtual {p0, v3}, Lcom/holy/dash/MainActivity$Bridge;->onUi(Ljava/lang/Runnable;)V

    goto :goto_9

    .line 1255
    :cond_25
    const-string v0, ";"

    invoke-virtual {p2, v0}, Ljava/lang/String;->split(Ljava/lang/String;)[Ljava/lang/String;

    move-result-object v0

    aget-object v0, v0, v3

    invoke-virtual {v0}, Ljava/lang/String;->trim()Ljava/lang/String;

    move-result-object v0

    sget-object v2, Ljava/util/Locale;->ROOT:Ljava/util/Locale;

    invoke-virtual {v0, v2}, Ljava/lang/String;->toLowerCase(Ljava/util/Locale;)Ljava/lang/String;

    move-result-object v0

    goto :goto_18
.end method

.method public setBg(Ljava/lang/String;)V
    .registers 3
    .annotation runtime Landroid/webkit/JavascriptInterface;
    .end annotation

    .prologue
    .line 1235
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity$Bridge;->ok()Z

    move-result v0

    if-eqz v0, :cond_8

    if-nez p1, :cond_9

    .line 1237
    :cond_8
    :goto_8
    return-void

    .line 1236
    :cond_9
    new-instance v0, Lcom/holy/dash/MainActivity$Bridge$12;

    invoke-direct {v0, p0, p1}, Lcom/holy/dash/MainActivity$Bridge$12;-><init>(Lcom/holy/dash/MainActivity$Bridge;Ljava/lang/String;)V

    invoke-virtual {p0, v0}, Lcom/holy/dash/MainActivity$Bridge;->onUi(Ljava/lang/Runnable;)V

    goto :goto_8
.end method

.method public setBio(Ljava/lang/String;)V
    .registers 4
    .annotation runtime Landroid/webkit/JavascriptInterface;
    .end annotation

    .prologue
    .line 1182
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity$Bridge;->ok()Z

    move-result v0

    if-eqz v0, :cond_28

    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-static {v0}, Lcom/holy/dash/Prefs;->lock(Landroid/content/Context;)Z

    move-result v0

    if-eqz v0, :cond_28

    if-eqz p1, :cond_28

    invoke-virtual {p1}, Ljava/lang/String;->length()I

    move-result v0

    const/16 v1, 0x14

    if-lt v0, v1, :cond_28

    invoke-virtual {p1}, Ljava/lang/String;->length()I

    move-result v0

    const/16 v1, 0xc8

    if-gt v0, v1, :cond_28

    const-string v0, "[A-Za-z0-9_\\-]+"

    invoke-virtual {p1, v0}, Ljava/lang/String;->matches(Ljava/lang/String;)Z

    move-result v0

    if-nez v0, :cond_29

    .line 1184
    :cond_28
    :goto_28
    return-void

    .line 1183
    :cond_29
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-static {v0, p1}, Lcom/holy/dash/Prefs;->setBio(Landroid/content/Context;Ljava/lang/String;)V

    goto :goto_28
.end method

.method public setFps(I)V
    .registers 3
    .annotation runtime Landroid/webkit/JavascriptInterface;
    .end annotation

    .prologue
    .line 1205
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity$Bridge;->ok()Z

    move-result v0

    if-eqz v0, :cond_c

    invoke-static {p1}, Lcom/holy/dash/Hz;->valid(I)Z

    move-result v0

    if-nez v0, :cond_d

    .line 1213
    :cond_c
    :goto_c
    return-void

    .line 1206
    :cond_d
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-static {v0, p1}, Lcom/holy/dash/Prefs;->setFps(Landroid/content/Context;I)V

    .line 1207
    new-instance v0, Lcom/holy/dash/MainActivity$Bridge$9;

    invoke-direct {v0, p0, p1}, Lcom/holy/dash/MainActivity$Bridge$9;-><init>(Lcom/holy/dash/MainActivity$Bridge;I)V

    invoke-virtual {p0, v0}, Lcom/holy/dash/MainActivity$Bridge;->onUi(Ljava/lang/Runnable;)V

    goto :goto_c
.end method

.method public navBar()Z
    .registers 2
    .annotation runtime Landroid/webkit/JavascriptInterface;
    .end annotation

    .prologue
    .line 1220
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-static {v0}, Lcom/holy/dash/Prefs;->navBar(Landroid/content/Context;)Z

    move-result v0

    return v0
.end method

.method public setNavBar(Z)V
    .registers 3
    .annotation runtime Landroid/webkit/JavascriptInterface;
    .end annotation

    .prologue
    .line 1224
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity$Bridge;->ok()Z

    move-result v0

    if-eqz v0, :cond_e

    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-static {v0, p1}, Lcom/holy/dash/Prefs;->setNavBar(Landroid/content/Context;Z)V

    new-instance v0, Lcom/holy/dash/MainActivity$Bridge$16;

    invoke-direct {v0, p0}, Lcom/holy/dash/MainActivity$Bridge$16;-><init>(Lcom/holy/dash/MainActivity$Bridge;)V

    invoke-virtual {p0, v0}, Lcom/holy/dash/MainActivity$Bridge;->onUi(Ljava/lang/Runnable;)V

    :cond_e
    return-void
.end method

.method public setHideLock(Z)V
    .registers 3
    .annotation runtime Landroid/webkit/JavascriptInterface;
    .end annotation

    .prologue
    .line 1159
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity$Bridge;->ok()Z

    move-result v0

    if-eqz v0, :cond_b

    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-static {v0, p1}, Lcom/holy/dash/Prefs;->setHideOnLock(Landroid/content/Context;Z)V

    :cond_b
    return-void
.end method

.method public setLock(Z)V
    .registers 3
    .annotation runtime Landroid/webkit/JavascriptInterface;
    .end annotation

    .prologue
    .line 1164
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity$Bridge;->ok()Z

    move-result v0

    if-nez v0, :cond_7

    .line 1177
    :goto_6
    return-void

    .line 1165
    :cond_7
    new-instance v0, Lcom/holy/dash/MainActivity$Bridge$7;

    invoke-direct {v0, p0, p1}, Lcom/holy/dash/MainActivity$Bridge$7;-><init>(Lcom/holy/dash/MainActivity$Bridge;Z)V

    invoke-virtual {p0, v0}, Lcom/holy/dash/MainActivity$Bridge;->onUi(Ljava/lang/Runnable;)V

    goto :goto_6
.end method

.method public setWatch(Z)V
    .registers 3
    .annotation runtime Landroid/webkit/JavascriptInterface;
    .end annotation

    .prologue
    .line 1123
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity$Bridge;->ok()Z

    move-result v0

    if-nez v0, :cond_7

    .line 1131
    :goto_6
    return-void

    .line 1124
    :cond_7
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-static {v0, p1}, Lcom/holy/dash/Prefs;->setWatch(Landroid/content/Context;Z)V

    .line 1125
    new-instance v0, Lcom/holy/dash/MainActivity$Bridge$2;

    invoke-direct {v0, p0, p1}, Lcom/holy/dash/MainActivity$Bridge$2;-><init>(Lcom/holy/dash/MainActivity$Bridge;Z)V

    invoke-virtual {p0, v0}, Lcom/holy/dash/MainActivity$Bridge;->onUi(Ljava/lang/Runnable;)V

    goto :goto_6
.end method

.method public shareFile(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V
    .registers 11
    .annotation runtime Landroid/webkit/JavascriptInterface;
    .end annotation

    .prologue
    const/4 v1, 0x0

    .line 1273
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity$Bridge;->ok()Z

    move-result v0

    if-eqz v0, :cond_9

    if-nez p3, :cond_a

    .line 1278
    :cond_9
    :goto_9
    return-void

    .line 1274
    :cond_a
    invoke-static {p1}, Lcom/holy/dash/MainActivity;->safeName(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    .line 1275
    if-eqz p2, :cond_16

    invoke-virtual {p2}, Ljava/lang/String;->isEmpty()Z

    move-result v0

    if-eqz v0, :cond_27

    :cond_16
    const-string v3, "application/octet-stream"

    .line 1276
    :goto_18
    invoke-static {p3, v1}, Landroid/util/Base64;->decode(Ljava/lang/String;I)[B

    move-result-object v4

    .line 1277
    new-instance v0, Lcom/holy/dash/MainActivity$Bridge$15;

    move-object v1, p0

    move-object v5, p4

    invoke-direct/range {v0 .. v5}, Lcom/holy/dash/MainActivity$Bridge$15;-><init>(Lcom/holy/dash/MainActivity$Bridge;Ljava/lang/String;Ljava/lang/String;[BLjava/lang/String;)V

    invoke-virtual {p0, v0}, Lcom/holy/dash/MainActivity$Bridge;->onUi(Ljava/lang/Runnable;)V

    goto :goto_9

    .line 1275
    :cond_27
    const-string v0, ";"

    invoke-virtual {p2, v0}, Ljava/lang/String;->split(Ljava/lang/String;)[Ljava/lang/String;

    move-result-object v0

    aget-object v0, v0, v1

    invoke-virtual {v0}, Ljava/lang/String;->trim()Ljava/lang/String;

    move-result-object v3

    goto :goto_18
.end method

.method public status()Ljava/lang/String;
    .registers 11
    .annotation runtime Landroid/webkit/JavascriptInterface;
    .end annotation

    .prologue
    const/4 v0, 0x1

    const/4 v1, 0x0

    .line 1067
    new-instance v3, Lorg/json/JSONObject;

    invoke-direct {v3}, Lorg/json/JSONObject;-><init>()V

    .line 1069
    :try_start_7
    const-string v2, "code"

    const/16 v4, 0xd

    invoke-virtual {v3, v2, v4}, Lorg/json/JSONObject;->put(Ljava/lang/String;I)Lorg/json/JSONObject;

    move-result-object v2

    const-string v4, "name"

    const-string v5, "2.2"

    invoke-virtual {v2, v4, v5}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    move-result-object v2

    const-string v4, "origin"

    iget-object v5, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v5, v5, Lcom/holy/dash/MainActivity;->origin:Ljava/lang/String;

    invoke-virtual {v2, v4, v5}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    move-result-object v2

    const-string v4, "paired"

    iget-object v5, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    .line 1070
    invoke-static {v5}, Lcom/holy/dash/Prefs;->paired(Landroid/content/Context;)Z

    move-result v5

    invoke-virtual {v2, v4, v5}, Lorg/json/JSONObject;->put(Ljava/lang/String;Z)Lorg/json/JSONObject;

    move-result-object v2

    const-string v4, "id"

    iget-object v5, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-static {v5}, Lcom/holy/dash/Prefs;->deviceId(Landroid/content/Context;)Ljava/lang/String;

    move-result-object v5

    invoke-virtual {v2, v4, v5}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    move-result-object v4

    const-string v5, "watching"

    iget-object v2, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    .line 1071
    invoke-static {v2}, Lcom/holy/dash/Prefs;->paired(Landroid/content/Context;)Z

    move-result v2

    if-eqz v2, :cond_133

    iget-object v2, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-static {v2}, Lcom/holy/dash/Prefs;->watch(Landroid/content/Context;)Z

    move-result v2

    if-eqz v2, :cond_133

    move v2, v0

    :goto_4c
    invoke-virtual {v4, v5, v2}, Lorg/json/JSONObject;->put(Ljava/lang/String;Z)Lorg/json/JSONObject;

    move-result-object v2

    const-string v4, "notif"

    iget-object v5, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    .line 1072
    invoke-virtual {v5}, Lcom/holy/dash/MainActivity;->notifAllowed()Z

    move-result v5

    invoke-virtual {v2, v4, v5}, Lorg/json/JSONObject;->put(Ljava/lang/String;Z)Lorg/json/JSONObject;

    move-result-object v2

    const-string v4, "battery"

    iget-object v5, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-virtual {v5}, Lcom/holy/dash/MainActivity;->batteryFree()Z

    move-result v5

    invoke-virtual {v2, v4, v5}, Lorg/json/JSONObject;->put(Ljava/lang/String;Z)Lorg/json/JSONObject;

    move-result-object v2

    const-string v4, "hideLock"

    iget-object v5, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-static {v5}, Lcom/holy/dash/Prefs;->hideOnLock(Landroid/content/Context;)Z

    move-result v5

    invoke-virtual {v2, v4, v5}, Lorg/json/JSONObject;->put(Ljava/lang/String;Z)Lorg/json/JSONObject;

    move-result-object v2

    const-string v4, "android"

    sget v5, Landroid/os/Build$VERSION;->SDK_INT:I

    .line 1073
    invoke-virtual {v2, v4, v5}, Lorg/json/JSONObject;->put(Ljava/lang/String;I)Lorg/json/JSONObject;

    move-result-object v2

    const-string v4, "watchHidden"

    iget-object v5, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-static {v5}, Lcom/holy/dash/Notif;->watchHidden(Landroid/content/Context;)Z

    move-result v5

    invoke-virtual {v2, v4, v5}, Lorg/json/JSONObject;->put(Ljava/lang/String;Z)Lorg/json/JSONObject;

    move-result-object v2

    const-string v4, "running"

    sget-boolean v5, Lcom/holy/dash/WatchService;->RUNNING:Z

    .line 1074
    invoke-virtual {v2, v4, v5}, Lorg/json/JSONObject;->put(Ljava/lang/String;Z)Lorg/json/JSONObject;

    move-result-object v2

    const-string v4, "lastPoll"

    iget-object v5, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-static {v5}, Lcom/holy/dash/Prefs;->lastPoll(Landroid/content/Context;)J

    move-result-wide v6

    const-wide/16 v8, 0x3e8

    div-long/2addr v6, v8

    invoke-virtual {v2, v4, v6, v7}, Lorg/json/JSONObject;->put(Ljava/lang/String;J)Lorg/json/JSONObject;

    move-result-object v4

    const-string v5, "maker"

    .line 1075
    sget-object v2, Landroid/os/Build;->MANUFACTURER:Ljava/lang/String;

    if-nez v2, :cond_136

    const-string v2, ""

    :goto_a7
    invoke-virtual {v4, v5, v2}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    move-result-object v2

    const-string v4, "strict"

    invoke-static {}, Lcom/holy/dash/Oem;->strict()Z

    move-result v5

    invoke-virtual {v2, v4, v5}, Lorg/json/JSONObject;->put(Ljava/lang/String;Z)Lorg/json/JSONObject;

    move-result-object v2

    const-string v4, "lock"

    iget-object v5, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    .line 1076
    invoke-static {v5}, Lcom/holy/dash/Prefs;->lock(Landroid/content/Context;)Z

    move-result v5

    invoke-virtual {v2, v4, v5}, Lorg/json/JSONObject;->put(Ljava/lang/String;Z)Lorg/json/JSONObject;

    move-result-object v2

    const-string v4, "lockOk"

    iget-object v5, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-virtual {v5}, Lcom/holy/dash/MainActivity;->canAuth()Z

    move-result v5

    invoke-virtual {v2, v4, v5}, Lorg/json/JSONObject;->put(Ljava/lang/String;Z)Lorg/json/JSONObject;

    move-result-object v2

    const-string v4, "bio"

    iget-object v5, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-virtual {v5}, Lcom/holy/dash/MainActivity;->hasBio()Z

    move-result v5

    invoke-virtual {v2, v4, v5}, Lorg/json/JSONObject;->put(Ljava/lang/String;Z)Lorg/json/JSONObject;

    move-result-object v2

    const-string v4, "bioKey"

    iget-object v5, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    .line 1077
    invoke-static {v5}, Lcom/holy/dash/Prefs;->lock(Landroid/content/Context;)Z

    move-result v5

    if-eqz v5, :cond_13a

    iget-object v5, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-static {v5}, Lcom/holy/dash/Prefs;->bio(Landroid/content/Context;)Ljava/lang/String;

    move-result-object v5

    invoke-virtual {v5}, Ljava/lang/String;->isEmpty()Z

    move-result v5

    if-nez v5, :cond_13a

    :goto_ef
    invoke-virtual {v2, v4, v0}, Lorg/json/JSONObject;->put(Ljava/lang/String;Z)Lorg/json/JSONObject;

    move-result-object v0

    const-string v1, "fps"

    iget-object v2, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    .line 1078
    invoke-static {v2}, Lcom/holy/dash/Prefs;->fps(Landroid/content/Context;)I

    move-result v2

    invoke-virtual {v0, v1, v2}, Lorg/json/JSONObject;->put(Ljava/lang/String;I)Lorg/json/JSONObject;

    move-result-object v0

    const-string v1, "hz"

    iget-object v2, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-static {v2}, Lcom/holy/dash/Hz;->now(Landroid/app/Activity;)I

    move-result v2

    invoke-virtual {v0, v1, v2}, Lorg/json/JSONObject;->put(Ljava/lang/String;I)Lorg/json/JSONObject;

    move-result-object v0

    const-string v1, "rates"

    iget-object v2, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-static {v2}, Lcom/holy/dash/Hz;->rates(Landroid/app/Activity;)Lorg/json/JSONArray;

    move-result-object v2

    invoke-virtual {v0, v1, v2}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    move-result-object v0

    const-string v1, "widget"

    iget-object v2, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    .line 1079
    invoke-static {v2}, Lcom/holy/dash/HolyWidget;->count(Landroid/content/Context;)I

    move-result v2

    invoke-virtual {v0, v1, v2}, Lorg/json/JSONObject;->put(Ljava/lang/String;I)Lorg/json/JSONObject;

    move-result-object v0

    const-string v1, "widgetPin"

    iget-object v2, p0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-static {v2}, Lcom/holy/dash/HolyWidget;->canPin(Landroid/content/Context;)Z

    move-result v2

    invoke-virtual {v0, v1, v2}, Lorg/json/JSONObject;->put(Ljava/lang/String;Z)Lorg/json/JSONObject;
    :try_end_12e
    .catch Ljava/lang/Exception; {:try_start_7 .. :try_end_12e} :catch_13c

    .line 1083
    :goto_12e
    invoke-virtual {v3}, Lorg/json/JSONObject;->toString()Ljava/lang/String;

    move-result-object v0

    return-object v0

    :cond_133
    move v2, v1

    .line 1071
    goto/16 :goto_4c

    .line 1075
    :cond_136
    :try_start_136
    sget-object v2, Landroid/os/Build;->MANUFACTURER:Ljava/lang/String;
    :try_end_138
    .catch Ljava/lang/Exception; {:try_start_136 .. :try_end_138} :catch_13c

    goto/16 :goto_a7

    :cond_13a
    move v0, v1

    .line 1077
    goto :goto_ef

    .line 1080
    :catch_13c
    move-exception v0

    goto :goto_12e
.end method

.method public watchSettings()V
    .registers 2
    .annotation runtime Landroid/webkit/JavascriptInterface;
    .end annotation

    .prologue
    .line 1154
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity$Bridge;->ok()Z

    move-result v0

    if-nez v0, :cond_7

    .line 1156
    :goto_6
    return-void

    .line 1155
    :cond_7
    new-instance v0, Lcom/holy/dash/MainActivity$Bridge$6;

    invoke-direct {v0, p0}, Lcom/holy/dash/MainActivity$Bridge$6;-><init>(Lcom/holy/dash/MainActivity$Bridge;)V

    invoke-virtual {p0, v0}, Lcom/holy/dash/MainActivity$Bridge;->onUi(Ljava/lang/Runnable;)V

    goto :goto_6
.end method
