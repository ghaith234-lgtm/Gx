.class Lcom/holy/dash/MainActivity$4;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Landroid/view/ViewTreeObserver$OnGlobalLayoutListener;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/MainActivity;->insets()V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$0:Lcom/holy/dash/MainActivity;


# direct methods
.method constructor <init>(Lcom/holy/dash/MainActivity;)V
    .registers 2

    .prologue
    .line 226
    iput-object p1, p0, Lcom/holy/dash/MainActivity$4;->this$0:Lcom/holy/dash/MainActivity;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public onGlobalLayout()V
    .registers 4

    .prologue
    .line 228
    new-instance v0, Landroid/graphics/Rect;

    invoke-direct {v0}, Landroid/graphics/Rect;-><init>()V

    .line 229
    iget-object v1, p0, Lcom/holy/dash/MainActivity$4;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v1, v1, Lcom/holy/dash/MainActivity;->root:Landroid/widget/FrameLayout;

    invoke-virtual {v1, v0}, Landroid/widget/FrameLayout;->getWindowVisibleDisplayFrame(Landroid/graphics/Rect;)V

    .line 230
    iget-object v1, p0, Lcom/holy/dash/MainActivity$4;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v1, v1, Lcom/holy/dash/MainActivity;->root:Landroid/widget/FrameLayout;

    invoke-virtual {v1}, Landroid/widget/FrameLayout;->getRootView()Landroid/view/View;

    move-result-object v1

    invoke-virtual {v1}, Landroid/view/View;->getHeight()I

    move-result v1

    .line 231
    iget v0, v0, Landroid/graphics/Rect;->bottom:I

    sub-int v0, v1, v0

    .line 232
    iget-object v1, p0, Lcom/holy/dash/MainActivity$4;->this$0:Lcom/holy/dash/MainActivity;

    const/high16 v2, 0x42f00000    # 120.0f

    invoke-virtual {v1, v2}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v1

    if-le v0, v1, :cond_36

    .line 233
    :goto_26
    iget-object v1, p0, Lcom/holy/dash/MainActivity$4;->this$0:Lcom/holy/dash/MainActivity;

    iget v1, v1, Lcom/holy/dash/MainActivity;->imeOld:I

    if-eq v0, v1, :cond_35

    iget-object v1, p0, Lcom/holy/dash/MainActivity$4;->this$0:Lcom/holy/dash/MainActivity;

    iput v0, v1, Lcom/holy/dash/MainActivity;->imeOld:I

    iget-object v0, p0, Lcom/holy/dash/MainActivity$4;->this$0:Lcom/holy/dash/MainActivity;

    invoke-virtual {v0}, Lcom/holy/dash/MainActivity;->applyOldPadding()V

    .line 234
    :cond_35
    return-void

    .line 232
    :cond_36
    const/4 v0, 0x0

    goto :goto_26
.end method
