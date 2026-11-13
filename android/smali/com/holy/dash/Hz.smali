.class final Lcom/holy/dash/Hz;
.super Ljava/lang/Object;
.source "Hz.java"


# static fields
.field static final CHOICES:[I


# direct methods
.method static constructor <clinit>()V
    .registers 1

    .prologue
    .line 16
    const/4 v0, 0x4

    new-array v0, v0, [I

    fill-array-data v0, :array_a

    sput-object v0, Lcom/holy/dash/Hz;->CHOICES:[I

    return-void

    nop

    :array_a
    .array-data 4
        0x1e
        0x3c
        0x78
        0xf0
    .end array-data
.end method

.method private constructor <init>()V
    .registers 1

    .prologue
    .line 14
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method static apply(Landroid/app/Activity;I)I
    .registers 12

    .prologue
    const/4 v4, 0x0

    .line 63
    :try_start_1
    sget v0, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v1, 0x17

    if-ge v0, v1, :cond_c

    invoke-static {p0}, Lcom/holy/dash/Hz;->now(Landroid/app/Activity;)I

    move-result v0

    .line 82
    :goto_b
    return v0

    .line 64
    :cond_c
    invoke-static {p0}, Lcom/holy/dash/Hz;->display(Landroid/app/Activity;)Landroid/view/Display;

    move-result-object v0

    .line 65
    invoke-virtual {v0}, Landroid/view/Display;->getMode()Landroid/view/Display$Mode;

    move-result-object v5

    .line 66
    invoke-virtual {v0}, Landroid/view/Display;->getSupportedModes()[Landroid/view/Display$Mode;

    move-result-object v6

    array-length v7, v6

    const/4 v1, 0x0

    move v3, v1

    move-object v0, v4

    move-object v2, v4

    :goto_1d
    if-ge v3, v7, :cond_5c

    aget-object v1, v6, v3

    .line 67
    invoke-virtual {v1}, Landroid/view/Display$Mode;->getPhysicalWidth()I

    move-result v4

    invoke-virtual {v5}, Landroid/view/Display$Mode;->getPhysicalWidth()I

    move-result v8

    if-ne v4, v8, :cond_35

    invoke-virtual {v1}, Landroid/view/Display$Mode;->getPhysicalHeight()I

    move-result v4

    invoke-virtual {v5}, Landroid/view/Display$Mode;->getPhysicalHeight()I

    move-result v8

    if-eq v4, v8, :cond_39

    .line 66
    :cond_35
    :goto_35
    add-int/lit8 v1, v3, 0x1

    move v3, v1

    goto :goto_1d

    .line 68
    :cond_39
    invoke-virtual {v1}, Landroid/view/Display$Mode;->getRefreshRate()F

    move-result v4

    .line 69
    int-to-float v8, p1

    const/high16 v9, 0x3f000000    # 0.5f

    add-float/2addr v8, v9

    cmpg-float v8, v4, v8

    if-gtz v8, :cond_50

    if-eqz v2, :cond_4f

    invoke-virtual {v2}, Landroid/view/Display$Mode;->getRefreshRate()F

    move-result v8

    cmpl-float v8, v4, v8

    if-lez v8, :cond_50

    :cond_4f
    move-object v2, v1

    .line 70
    :cond_50
    if-eqz v0, :cond_5a

    invoke-virtual {v0}, Landroid/view/Display$Mode;->getRefreshRate()F

    move-result v8

    cmpg-float v4, v4, v8

    if-gez v4, :cond_35

    :cond_5a
    move-object v0, v1

    goto :goto_35

    .line 72
    :cond_5c
    if-nez v2, :cond_a3

    .line 73
    :goto_5e
    if-nez v0, :cond_65

    invoke-static {p0}, Lcom/holy/dash/Hz;->now(Landroid/app/Activity;)I

    move-result v0

    goto :goto_b

    .line 74
    :cond_65
    invoke-virtual {p0}, Landroid/app/Activity;->getWindow()Landroid/view/Window;

    move-result-object v1

    invoke-virtual {v1}, Landroid/view/Window;->getAttributes()Landroid/view/WindowManager$LayoutParams;

    move-result-object v1

    .line 75
    iget v2, v1, Landroid/view/WindowManager$LayoutParams;->preferredDisplayModeId:I

    invoke-virtual {v0}, Landroid/view/Display$Mode;->getModeId()I

    move-result v3

    if-ne v2, v3, :cond_7f

    iget v2, v1, Landroid/view/WindowManager$LayoutParams;->preferredRefreshRate:F

    invoke-virtual {v0}, Landroid/view/Display$Mode;->getRefreshRate()F

    move-result v3

    cmpl-float v2, v2, v3

    if-eqz v2, :cond_92

    .line 76
    :cond_7f
    invoke-virtual {v0}, Landroid/view/Display$Mode;->getModeId()I

    move-result v2

    iput v2, v1, Landroid/view/WindowManager$LayoutParams;->preferredDisplayModeId:I

    .line 77
    invoke-virtual {v0}, Landroid/view/Display$Mode;->getRefreshRate()F

    move-result v2

    iput v2, v1, Landroid/view/WindowManager$LayoutParams;->preferredRefreshRate:F

    .line 78
    invoke-virtual {p0}, Landroid/app/Activity;->getWindow()Landroid/view/Window;

    move-result-object v2

    invoke-virtual {v2, v1}, Landroid/view/Window;->setAttributes(Landroid/view/WindowManager$LayoutParams;)V

    .line 80
    :cond_92
    invoke-virtual {v0}, Landroid/view/Display$Mode;->getRefreshRate()F

    move-result v0

    invoke-static {v0}, Ljava/lang/Math;->round(F)I
    :try_end_99
    .catch Ljava/lang/Exception; {:try_start_1 .. :try_end_99} :catch_9c

    move-result v0

    goto/16 :goto_b

    .line 81
    :catch_9c
    move-exception v0

    .line 82
    invoke-static {p0}, Lcom/holy/dash/Hz;->now(Landroid/app/Activity;)I

    move-result v0

    goto/16 :goto_b

    :cond_a3
    move-object v0, v2

    goto :goto_5e
.end method

.method static display(Landroid/app/Activity;)Landroid/view/Display;
    .registers 3

    .prologue
    .line 25
    sget v0, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v1, 0x1e

    if-lt v0, v1, :cond_d

    .line 26
    invoke-virtual {p0}, Landroid/app/Activity;->getDisplay()Landroid/view/Display;

    move-result-object v0

    .line 27
    if-eqz v0, :cond_d

    .line 29
    :goto_c
    return-object v0

    :cond_d
    invoke-virtual {p0}, Landroid/app/Activity;->getWindowManager()Landroid/view/WindowManager;

    move-result-object v0

    invoke-interface {v0}, Landroid/view/WindowManager;->getDefaultDisplay()Landroid/view/Display;

    move-result-object v0

    goto :goto_c
.end method

.method static now(Landroid/app/Activity;)I
    .registers 2

    .prologue
    .line 54
    :try_start_0
    invoke-static {p0}, Lcom/holy/dash/Hz;->display(Landroid/app/Activity;)Landroid/view/Display;

    move-result-object v0

    invoke-virtual {v0}, Landroid/view/Display;->getRefreshRate()F

    move-result v0

    invoke-static {v0}, Ljava/lang/Math;->round(F)I
    :try_end_b
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_b} :catch_d

    move-result v0

    .line 56
    :goto_c
    return v0

    .line 55
    :catch_d
    move-exception v0

    .line 56
    const/4 v0, 0x0

    goto :goto_c
.end method

.method static rates(Landroid/app/Activity;)Lorg/json/JSONArray;
    .registers 10

    .prologue
    .line 34
    new-instance v1, Lorg/json/JSONArray;

    invoke-direct {v1}, Lorg/json/JSONArray;-><init>()V

    .line 36
    :try_start_5
    invoke-static {p0}, Lcom/holy/dash/Hz;->display(Landroid/app/Activity;)Landroid/view/Display;

    move-result-object v0

    .line 37
    new-instance v2, Ljava/util/TreeSet;

    invoke-direct {v2}, Ljava/util/TreeSet;-><init>()V

    .line 38
    sget v3, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v4, 0x17

    if-lt v3, v4, :cond_48

    .line 39
    invoke-virtual {v0}, Landroid/view/Display;->getMode()Landroid/view/Display$Mode;

    move-result-object v3

    .line 40
    invoke-virtual {v0}, Landroid/view/Display;->getSupportedModes()[Landroid/view/Display$Mode;

    move-result-object v4

    array-length v5, v4

    const/4 v0, 0x0

    :goto_1e
    if-ge v0, v5, :cond_57

    aget-object v6, v4, v0

    .line 41
    invoke-virtual {v6}, Landroid/view/Display$Mode;->getPhysicalWidth()I

    move-result v7

    invoke-virtual {v3}, Landroid/view/Display$Mode;->getPhysicalWidth()I

    move-result v8

    if-ne v7, v8, :cond_45

    invoke-virtual {v6}, Landroid/view/Display$Mode;->getPhysicalHeight()I

    move-result v7

    invoke-virtual {v3}, Landroid/view/Display$Mode;->getPhysicalHeight()I

    move-result v8

    if-ne v7, v8, :cond_45

    invoke-virtual {v6}, Landroid/view/Display$Mode;->getRefreshRate()F

    move-result v6

    invoke-static {v6}, Ljava/lang/Math;->round(F)I

    move-result v6

    invoke-static {v6}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;

    move-result-object v6

    invoke-virtual {v2, v6}, Ljava/util/TreeSet;->add(Ljava/lang/Object;)Z

    .line 40
    :cond_45
    add-int/lit8 v0, v0, 0x1

    goto :goto_1e

    .line 43
    :cond_48
    invoke-virtual {v0}, Landroid/view/Display;->getRefreshRate()F

    move-result v0

    invoke-static {v0}, Ljava/lang/Math;->round(F)I

    move-result v0

    invoke-static {v0}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;

    move-result-object v0

    invoke-virtual {v2, v0}, Ljava/util/TreeSet;->add(Ljava/lang/Object;)Z

    .line 45
    :cond_57
    invoke-virtual {v2}, Ljava/util/TreeSet;->iterator()Ljava/util/Iterator;

    move-result-object v2

    :goto_5b
    invoke-interface {v2}, Ljava/util/Iterator;->hasNext()Z

    move-result v0

    if-eqz v0, :cond_6c

    invoke-interface {v2}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Ljava/lang/Integer;

    invoke-virtual {v1, v0}, Lorg/json/JSONArray;->put(Ljava/lang/Object;)Lorg/json/JSONArray;
    :try_end_6a
    .catch Ljava/lang/Exception; {:try_start_5 .. :try_end_6a} :catch_6b

    goto :goto_5b

    .line 46
    :catch_6b
    move-exception v0

    .line 49
    :cond_6c
    return-object v1
.end method

.method static valid(I)Z
    .registers 6

    .prologue
    const/4 v0, 0x0

    .line 19
    sget-object v2, Lcom/holy/dash/Hz;->CHOICES:[I

    array-length v3, v2

    move v1, v0

    :goto_5
    if-ge v1, v3, :cond_c

    aget v4, v2, v1

    if-ne v4, p0, :cond_d

    const/4 v0, 0x1

    .line 20
    :cond_c
    return v0

    .line 19
    :cond_d
    add-int/lit8 v1, v1, 0x1

    goto :goto_5
.end method
