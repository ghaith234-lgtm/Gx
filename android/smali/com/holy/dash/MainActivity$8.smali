.class Lcom/holy/dash/MainActivity$8;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Landroid/view/View$OnLongClickListener;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/MainActivity;->setupLongPress(Ljava/lang/String;)V
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
    .line 383
    iput-object p1, p0, Lcom/holy/dash/MainActivity$8;->this$0:Lcom/holy/dash/MainActivity;

    iput-object p2, p0, Lcom/holy/dash/MainActivity$8;->val$o:Ljava/lang/String;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public onLongClick(Landroid/view/View;)Z
    .registers 4

    .prologue
    .line 384
    iget-object v0, p0, Lcom/holy/dash/MainActivity$8;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v1, p0, Lcom/holy/dash/MainActivity$8;->val$o:Ljava/lang/String;

    invoke-virtual {v0, v1}, Lcom/holy/dash/MainActivity;->useOrigin(Ljava/lang/String;)V

    const/4 v0, 0x1

    return v0
.end method
