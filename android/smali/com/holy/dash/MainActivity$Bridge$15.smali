.class Lcom/holy/dash/MainActivity$Bridge$15;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/MainActivity$Bridge;->shareFile(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V
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

.field final synthetic val$text:Ljava/lang/String;


# direct methods
.method constructor <init>(Lcom/holy/dash/MainActivity$Bridge;Ljava/lang/String;Ljava/lang/String;[BLjava/lang/String;)V
    .registers 6
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .prologue
    .line 1277
    iput-object p1, p0, Lcom/holy/dash/MainActivity$Bridge$15;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iput-object p2, p0, Lcom/holy/dash/MainActivity$Bridge$15;->val$n:Ljava/lang/String;

    iput-object p3, p0, Lcom/holy/dash/MainActivity$Bridge$15;->val$m:Ljava/lang/String;

    iput-object p4, p0, Lcom/holy/dash/MainActivity$Bridge$15;->val$data:[B

    iput-object p5, p0, Lcom/holy/dash/MainActivity$Bridge$15;->val$text:Ljava/lang/String;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .registers 6

    .prologue
    .line 1277
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge$15;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v1, p0, Lcom/holy/dash/MainActivity$Bridge$15;->val$n:Ljava/lang/String;

    iget-object v2, p0, Lcom/holy/dash/MainActivity$Bridge$15;->val$m:Ljava/lang/String;

    iget-object v3, p0, Lcom/holy/dash/MainActivity$Bridge$15;->val$data:[B

    iget-object v4, p0, Lcom/holy/dash/MainActivity$Bridge$15;->val$text:Ljava/lang/String;

    invoke-virtual {v0, v1, v2, v3, v4}, Lcom/holy/dash/MainActivity;->share(Ljava/lang/String;Ljava/lang/String;[BLjava/lang/String;)V

    return-void
.end method
