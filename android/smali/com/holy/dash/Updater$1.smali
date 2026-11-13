.class Lcom/holy/dash/Updater$1;
.super Ljava/lang/Object;
.source "Updater.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/Updater;->check(Landroid/app/Activity;Z)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic val$a:Landroid/app/Activity;

.field final synthetic val$manual:Z

.field final synthetic val$origin:Ljava/lang/String;


# direct methods
.method constructor <init>(Ljava/lang/String;Landroid/app/Activity;Z)V
    .registers 4
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .prologue
    .line 55
    iput-object p1, p0, Lcom/holy/dash/Updater$1;->val$origin:Ljava/lang/String;

    iput-object p2, p0, Lcom/holy/dash/Updater$1;->val$a:Landroid/app/Activity;

    iput-boolean p3, p0, Lcom/holy/dash/Updater$1;->val$manual:Z

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .registers 5

    .prologue
    .line 58
    :try_start_0
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    iget-object v1, p0, Lcom/holy/dash/Updater$1;->val$origin:Ljava/lang/String;

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v1, "/api/app/info"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    iget-object v1, p0, Lcom/holy/dash/Updater$1;->val$a:Landroid/app/Activity;

    iget-object v2, p0, Lcom/holy/dash/Updater$1;->val$origin:Ljava/lang/String;

    invoke-static {v1, v2}, Lcom/holy/dash/Updater;->headers(Landroid/content/Context;Ljava/lang/String;)Ljava/util/Map;

    move-result-object v1

    const/16 v2, 0x2ee0

    const/4 v3, 0x0

    invoke-static {v0, v1, v2, v3}, Lcom/holy/dash/Net;->get(Ljava/lang/String;Ljava/util/Map;I[Ljava/net/HttpURLConnection;)Lcom/holy/dash/Net$Resp;

    move-result-object v0

    .line 59
    iget v1, v0, Lcom/holy/dash/Net$Resp;->code:I

    const/16 v2, 0xc8

    if-eq v1, v2, :cond_55

    new-instance v1, Ljava/io/IOException;

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    const-string v3, "HTTP "

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    iget v0, v0, Lcom/holy/dash/Net$Resp;->code:I

    invoke-virtual {v2, v0}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-direct {v1, v0}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw v1
    :try_end_45
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_45} :catch_45

    .line 69
    :catch_45
    move-exception v0

    .line 70
    iget-boolean v0, p0, Lcom/holy/dash/Updater$1;->val$manual:Z

    if-eqz v0, :cond_54

    iget-object v0, p0, Lcom/holy/dash/Updater$1;->val$a:Landroid/app/Activity;

    new-instance v1, Lcom/holy/dash/Updater$1$2;

    invoke-direct {v1, p0}, Lcom/holy/dash/Updater$1$2;-><init>(Lcom/holy/dash/Updater$1;)V

    invoke-virtual {v0, v1}, Landroid/app/Activity;->runOnUiThread(Ljava/lang/Runnable;)V

    .line 74
    :cond_54
    :goto_54
    return-void

    .line 60
    :cond_55
    :try_start_55
    new-instance v1, Lorg/json/JSONObject;

    iget-object v0, v0, Lcom/holy/dash/Net$Resp;->body:Ljava/lang/String;

    invoke-direct {v1, v0}, Lorg/json/JSONObject;-><init>(Ljava/lang/String;)V

    const-string v0, "apk"

    invoke-virtual {v1, v0}, Lorg/json/JSONObject;->getJSONObject(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v0

    .line 61
    const-string v1, "code"

    const/4 v2, 0x0

    invoke-virtual {v0, v1, v2}, Lorg/json/JSONObject;->optInt(Ljava/lang/String;I)I

    move-result v1

    .line 62
    iget-object v2, p0, Lcom/holy/dash/Updater$1;->val$a:Landroid/app/Activity;

    new-instance v3, Lcom/holy/dash/Updater$1$1;

    invoke-direct {v3, p0, v1, v0}, Lcom/holy/dash/Updater$1$1;-><init>(Lcom/holy/dash/Updater$1;ILorg/json/JSONObject;)V

    invoke-virtual {v2, v3}, Landroid/app/Activity;->runOnUiThread(Ljava/lang/Runnable;)V
    :try_end_73
    .catch Ljava/lang/Exception; {:try_start_55 .. :try_end_73} :catch_45

    goto :goto_54
.end method
