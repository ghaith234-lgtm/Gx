.class Lcom/holy/dash/MainActivity$18$1;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/MainActivity$18;->run()V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$1:Lcom/holy/dash/MainActivity$18;

.field final synthetic val$fc:I

.field final synthetic val$fm:I

.field final synthetic val$ft:Ljava/lang/String;


# direct methods
.method constructor <init>(Lcom/holy/dash/MainActivity$18;ILjava/lang/String;I)V
    .registers 5
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .prologue
    .line 945
    iput-object p1, p0, Lcom/holy/dash/MainActivity$18$1;->this$1:Lcom/holy/dash/MainActivity$18;

    iput p2, p0, Lcom/holy/dash/MainActivity$18$1;->val$fc:I

    iput-object p3, p0, Lcom/holy/dash/MainActivity$18$1;->val$ft:Ljava/lang/String;

    iput p4, p0, Lcom/holy/dash/MainActivity$18$1;->val$fm:I

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .registers 6

    .prologue
    .line 945
    iget-object v0, p0, Lcom/holy/dash/MainActivity$18$1;->this$1:Lcom/holy/dash/MainActivity$18;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$18;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v1, p0, Lcom/holy/dash/MainActivity$18$1;->this$1:Lcom/holy/dash/MainActivity$18;

    iget-object v1, v1, Lcom/holy/dash/MainActivity$18;->val$o:Ljava/lang/String;

    iget v2, p0, Lcom/holy/dash/MainActivity$18$1;->val$fc:I

    iget-object v3, p0, Lcom/holy/dash/MainActivity$18$1;->val$ft:Ljava/lang/String;

    iget v4, p0, Lcom/holy/dash/MainActivity$18$1;->val$fm:I

    invoke-virtual {v0, v1, v2, v3, v4}, Lcom/holy/dash/MainActivity;->bioDone(Ljava/lang/String;ILjava/lang/String;I)V

    return-void
.end method
