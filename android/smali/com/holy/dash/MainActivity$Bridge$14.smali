.class Lcom/holy/dash/MainActivity$Bridge$14;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/MainActivity$Bridge;->saveFile(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$1:Lcom/holy/dash/MainActivity$Bridge;

.field final synthetic val$data:[B

.field final synthetic val$m:Ljava/lang/String;

.field final synthetic val$n:Ljava/lang/String;


# direct methods
.method constructor <init>(Lcom/holy/dash/MainActivity$Bridge;[BLjava/lang/String;Ljava/lang/String;)V
    .registers 5
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .prologue
    .line 1257
    iput-object p1, p0, Lcom/holy/dash/MainActivity$Bridge$14;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iput-object p2, p0, Lcom/holy/dash/MainActivity$Bridge$14;->val$data:[B

    iput-object p3, p0, Lcom/holy/dash/MainActivity$Bridge$14;->val$n:Ljava/lang/String;

    iput-object p4, p0, Lcom/holy/dash/MainActivity$Bridge$14;->val$m:Ljava/lang/String;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .registers 5

    .prologue
    .line 1259
    sget v0, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v1, 0x1d

    if-ge v0, v1, :cond_3c

    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge$14;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    const-string v1, "android.permission.WRITE_EXTERNAL_STORAGE"

    invoke-virtual {v0, v1}, Lcom/holy/dash/MainActivity;->checkSelfPermission(Ljava/lang/String;)I

    move-result v0

    if-eqz v0, :cond_3c

    .line 1260
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge$14;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v1, p0, Lcom/holy/dash/MainActivity$Bridge$14;->val$data:[B

    iput-object v1, v0, Lcom/holy/dash/MainActivity;->pendingSave:[B

    .line 1261
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge$14;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v1, p0, Lcom/holy/dash/MainActivity$Bridge$14;->val$n:Ljava/lang/String;

    iput-object v1, v0, Lcom/holy/dash/MainActivity;->pendingSaveName:Ljava/lang/String;

    .line 1262
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge$14;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v1, p0, Lcom/holy/dash/MainActivity$Bridge$14;->val$m:Ljava/lang/String;

    iput-object v1, v0, Lcom/holy/dash/MainActivity;->pendingSaveMime:Ljava/lang/String;

    .line 1263
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge$14;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    const/4 v1, 0x1

    new-array v1, v1, [Ljava/lang/String;

    const/4 v2, 0x0

    const-string v3, "android.permission.WRITE_EXTERNAL_STORAGE"

    aput-object v3, v1, v2

    const/16 v2, 0xc

    invoke-virtual {v0, v1, v2}, Lcom/holy/dash/MainActivity;->requestPermissions([Ljava/lang/String;I)V

    .line 1267
    :goto_3b
    return-void

    .line 1266
    :cond_3c
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge$14;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v1, p0, Lcom/holy/dash/MainActivity$Bridge$14;->val$n:Ljava/lang/String;

    iget-object v2, p0, Lcom/holy/dash/MainActivity$Bridge$14;->val$m:Ljava/lang/String;

    iget-object v3, p0, Lcom/holy/dash/MainActivity$Bridge$14;->val$data:[B

    invoke-virtual {v0, v1, v2, v3}, Lcom/holy/dash/MainActivity;->saveNow(Ljava/lang/String;Ljava/lang/String;[B)V

    goto :goto_3b
.end method
