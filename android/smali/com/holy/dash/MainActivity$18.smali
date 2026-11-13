.class Lcom/holy/dash/MainActivity$18;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/MainActivity;->bioOpen()V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$0:Lcom/holy/dash/MainActivity;

.field final synthetic val$key:Ljava/lang/String;

.field final synthetic val$o:Ljava/lang/String;

.field final synthetic val$tok:Ljava/lang/String;


# direct methods
.method constructor <init>(Lcom/holy/dash/MainActivity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V
    .registers 5
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .prologue
    .line 925
    iput-object p1, p0, Lcom/holy/dash/MainActivity$18;->this$0:Lcom/holy/dash/MainActivity;

    iput-object p2, p0, Lcom/holy/dash/MainActivity$18;->val$tok:Ljava/lang/String;

    iput-object p3, p0, Lcom/holy/dash/MainActivity$18;->val$key:Ljava/lang/String;

    iput-object p4, p0, Lcom/holy/dash/MainActivity$18;->val$o:Ljava/lang/String;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .registers 8

    .prologue
    const/16 v0, 0x1e

    .line 927
    .line 928
    const/4 v1, 0x0

    .line 931
    :try_start_3
    new-instance v2, Ljava/util/HashMap;

    invoke-direct {v2}, Ljava/util/HashMap;-><init>()V

    .line 932
    const-string v3, "X-Holy-Device"

    iget-object v4, p0, Lcom/holy/dash/MainActivity$18;->val$tok:Ljava/lang/String;

    invoke-virtual {v2, v3, v4}, Ljava/util/HashMap;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;

    .line 933
    const-string v3, "X-Holy-Bio"

    iget-object v4, p0, Lcom/holy/dash/MainActivity$18;->val$key:Ljava/lang/String;

    invoke-virtual {v2, v3, v4}, Ljava/util/HashMap;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;

    .line 934
    new-instance v3, Ljava/lang/StringBuilder;

    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V

    iget-object v4, p0, Lcom/holy/dash/MainActivity$18;->val$o:Ljava/lang/String;

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    const-string v4, "/api/app/bio_unlock"

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    const-string v4, "{}"

    const/16 v5, 0x3a98

    invoke-static {v3, v2, v4, v5}, Lcom/holy/dash/Net;->post(Ljava/lang/String;Ljava/util/Map;Ljava/lang/String;I)Lcom/holy/dash/Net$Resp;

    move-result-object v3

    .line 935
    iget v2, v3, Lcom/holy/dash/Net$Resp;->code:I

    .line 936
    const/16 v4, 0xc8

    if-ne v2, v4, :cond_5d

    .line 937
    new-instance v4, Lorg/json/JSONObject;

    iget-object v3, v3, Lcom/holy/dash/Net$Resp;->body:Ljava/lang/String;

    invoke-direct {v4, v3}, Lorg/json/JSONObject;-><init>(Ljava/lang/String;)V

    .line 938
    const-string v3, "ok"

    invoke-virtual {v4, v3}, Lorg/json/JSONObject;->optBoolean(Ljava/lang/String;)Z

    move-result v3

    if-eqz v3, :cond_5d

    const-string v3, "tok"

    const-string v5, ""

    invoke-virtual {v4, v3, v5}, Lorg/json/JSONObject;->optString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    const/4 v3, 0x1

    const-string v5, "mins"

    const/16 v6, 0x1e

    invoke-virtual {v4, v5, v6}, Lorg/json/JSONObject;->optInt(Ljava/lang/String;I)I

    move-result v4

    invoke-static {v3, v4}, Ljava/lang/Math;->max(II)I
    :try_end_5c
    .catch Ljava/lang/Exception; {:try_start_3 .. :try_end_5c} :catch_6a

    move-result v0

    .line 945
    :cond_5d
    :goto_5d
    iget-object v3, p0, Lcom/holy/dash/MainActivity$18;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v3, v3, Lcom/holy/dash/MainActivity;->ui:Landroid/os/Handler;

    new-instance v4, Lcom/holy/dash/MainActivity$18$1;

    invoke-direct {v4, p0, v2, v1, v0}, Lcom/holy/dash/MainActivity$18$1;-><init>(Lcom/holy/dash/MainActivity$18;ILjava/lang/String;I)V

    invoke-virtual {v3, v4}, Landroid/os/Handler;->post(Ljava/lang/Runnable;)Z

    .line 946
    return-void

    .line 940
    :catch_6a
    move-exception v2

    .line 941
    const/4 v2, -0x1

    goto :goto_5d
.end method
