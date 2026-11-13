.class Lcom/holy/dash/MainActivity$7;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/MainActivity;->connect(Z)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$0:Lcom/holy/dash/MainActivity;

.field final synthetic val$o:Ljava/lang/String;


# direct methods
.method constructor <init>(Lcom/holy/dash/MainActivity;Ljava/lang/String;)V
    .registers 3
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .prologue
    .line 359
    iput-object p1, p0, Lcom/holy/dash/MainActivity$7;->this$0:Lcom/holy/dash/MainActivity;

    iput-object p2, p0, Lcom/holy/dash/MainActivity$7;->val$o:Ljava/lang/String;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .registers 6

    .prologue
    const/4 v0, 0x0

    .line 363
    :try_start_1
    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    iget-object v2, p0, Lcom/holy/dash/MainActivity$7;->val$o:Ljava/lang/String;

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v2, "/"

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    const/4 v2, 0x0

    const/16 v3, 0x1f40

    const/4 v4, 0x0

    invoke-static {v1, v2, v3, v4}, Lcom/holy/dash/Net;->get(Ljava/lang/String;Ljava/util/Map;I[Ljava/net/HttpURLConnection;)Lcom/holy/dash/Net$Resp;

    move-result-object v1

    .line 364
    iget v2, v1, Lcom/holy/dash/Net$Resp;->code:I

    const/16 v3, 0xc8

    if-ne v2, v3, :cond_39

    iget-object v2, v1, Lcom/holy/dash/Net$Resp;->body:Ljava/lang/String;

    const-string v3, "Holy"

    invoke-virtual {v2, v3}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z

    move-result v2

    if-nez v2, :cond_38

    iget-object v1, v1, Lcom/holy/dash/Net$Resp;->body:Ljava/lang/String;

    const-string v2, "holy"

    invoke-virtual {v1, v2}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    :try_end_35
    .catch Ljava/lang/Exception; {:try_start_1 .. :try_end_35} :catch_46

    move-result v1

    if-eqz v1, :cond_39

    :cond_38
    const/4 v0, 0x1

    .line 369
    :cond_39
    :goto_39
    iget-object v1, p0, Lcom/holy/dash/MainActivity$7;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v1, v1, Lcom/holy/dash/MainActivity;->ui:Landroid/os/Handler;

    new-instance v2, Lcom/holy/dash/MainActivity$7$1;

    invoke-direct {v2, p0, v0}, Lcom/holy/dash/MainActivity$7$1;-><init>(Lcom/holy/dash/MainActivity$7;Z)V

    invoke-virtual {v1, v2}, Landroid/os/Handler;->post(Ljava/lang/Runnable;)Z

    .line 377
    return-void

    .line 365
    :catch_46
    move-exception v1

    goto :goto_39
.end method
