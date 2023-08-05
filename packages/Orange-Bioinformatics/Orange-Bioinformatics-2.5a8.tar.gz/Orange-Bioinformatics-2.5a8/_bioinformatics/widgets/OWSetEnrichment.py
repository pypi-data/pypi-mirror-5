"""<name>Gene Set Enrichment</name>
<icon>icons/GeneSetEnrichment.svg</icon>
"""

from __future__ import absolute_import, with_statement

import math
from collections import defaultdict

from Orange.orng import orngEnviron, orngServerFiles
from Orange.orng.orngDataCaching import data_hints
from Orange.OrangeWidgets import OWGUI
from Orange.OrangeWidgets.OWGUI import LinkStyledItemDelegate, LinkRole
from Orange.OrangeWidgets.OWGUI import BarItemDelegate
from Orange.OrangeWidgets.OWWidget import *

from .. import obiGene, obiGeneSets, obiProb, obiTaxonomy

def _toPyObject(variant):
    val = variant.toPyObject()
    if isinstance(val, type(NotImplemented)): # PyQt 4.4 converts python int, floats ... to C types
        qtype = variant.type()
        if qtype == QVariant.Double:
            val, ok = variant.toDouble()
        elif qtype == QVariant.Int:
            val, ok = variant.toInt()
        elif qtype == QVariant.LongLong:
            val, ok = variant.toLongLong()
        elif qtype == QVariant.String:
            val = variant.toString()
    return val

class MyTreeWidget(QTreeWidget):
    def paintEvent(self, event):
        QTreeWidget.paintEvent(self, event)
        if getattr(self, "_userMessage", None):
            painter = QPainter(self.viewport())
            font = QFont(self.font())
            font.setPointSize(15)
            painter.setFont(font)
            painter.drawText(self.viewport().geometry(), Qt.AlignCenter, self._userMessage)
            painter.end()

class MyTreeWidgetItem(QTreeWidgetItem):
    def __lt__(self, other):
        if not self.treeWidget():
            return id(self) < id(other)
        column = self.treeWidget().sortColumn()
        if column == 4:
            lhs = _toPyObject(self.data(column, 42))
            rhs = _toPyObject(other.data(column, 42))
        else:
            lhs = _toPyObject(self.data(column, Qt.DisplayRole))
            rhs = _toPyObject(other.data(column, Qt.DisplayRole))
        return lhs < rhs

def name_or_none(id):
    """Return organism name for ncbi taxid or None if not found.
    """
    try:
        return obiTaxonomy.name(id)
    except obiTaxonomy.UnknownSpeciesIdentifier:
        return None

class OWSetEnrichment(OWWidget):
    settingsList = ["speciesIndex", "genesinrows", "geneattr", "categoriesCheckState"]
    contextHandlers = {"":DomainContextHandler("", ["speciesIndex", "genesinrows", "geneattr", "categoriesCheckState"])}

    def __init__(self, parent=None, signalManager=None, name="Gene Set Enrichment Analysis", **kwargs):
        OWWidget.__init__(self, parent, signalManager, name, **kwargs)
        self.inputs = [("Example Table", ExampleTable, self.setData, Default), ("Reference", ExampleTable, self.setReference)]
        self.outputs = [("Selected Examples", ExampleTable)]

        self.speciesIndex = 0
        self.genesinrows = False
        self.geneattr = 0
        self.geneMatcherSettings = [False, False, True, False]
        self.useReferenceData = False
        self.useMinCountFilter = True
        self.useMaxPValFilter = True
        self.minClusterCount = 0
        self.maxPValue = 0.01

        self.useFDR = True

        self.categoriesCheckState = {}

        self.loadSettings()

        if self.signalManager:
            self.signalManager.freeze(self).push()
        QTimer.singleShot(50, self.updateHierarchy)

        box = OWGUI.widgetBox(self.controlArea, "Info")
        self.infoBox = OWGUI.widgetLabel(box, "Info")
        self.infoBox.setText("No data on input")

        self.speciesComboBox = OWGUI.comboBox(self.controlArea, self,
                      "speciesIndex", "Species",
                      callback=lambda :self.data and self.updateAnnotations(),
                      debuggingEnabled=0)

        box = OWGUI.widgetBox(self.controlArea, "Gene names")
        self.geneAttrComboBox = OWGUI.comboBox(box, self, "geneattr",
                                "Gene attribute",
                                sendSelectedValue=0,
                                callback=self.updateAnnotations)

        cb = OWGUI.checkBox(box, self, "genesinrows", "Use attribute names",
                            callback=lambda :self.data and self.updateAnnotations(),
                            disables=[(-1, self.geneAttrComboBox)])
        cb.makeConsistent()

        OWGUI.button(box, self, "Gene matcher settings",
                     callback=self.updateGeneMatcherSettings,
                     tooltip="Open gene matching settings dialog",
                     debuggingEnabled=0)

        self.referenceRadioBox = OWGUI.radioButtonsInBox(self.controlArea,
                    self, "useReferenceData", ["Entire genome", "Reference set (input)"],
                    tooltips=["Use entire genome for reference",
                              "Use genes from Referece Examples input signal as reference"],
                    box="Reference", callback=self.updateAnnotations)

        box = OWGUI.widgetBox(self.controlArea, "Gene Sets")
        self.groupsWidget = QTreeWidget(self)
        self.groupsWidget.setHeaderLabels(["Category"])
        box.layout().addWidget(self.groupsWidget)

        hLayout = QHBoxLayout()
        hLayout.setSpacing(10)
        hWidget = OWGUI.widgetBox(self.mainArea, orientation=hLayout)
        sb, sbcb = OWGUI.spin(hWidget, self, "minClusterCount",
                              0, 100, label="Genes",
                              tooltip="Minimum gene count",
                              callback=self.filterAnnotationsChartView,
                              callbackOnReturn=True,
                              checked="useMinCountFilter",
                              checkCallback=self.filterAnnotationsChartView)

        dsp, dspcb = OWGUI.doubleSpin(hWidget, self,
                        "maxPValue", 0.0, 1.0, 0.0001,
                        label="FDR adjusted P-Value",
                        tooltip="Maximum (FDR adjusted) P-Value",
                        callback=self.filterAnnotationsChartView,
                        callbackOnReturn=True,
                        checked="useMaxPValFilter",
                        checkCallback=self.filterAnnotationsChartView)

        from Orange.OrangeWidgets import OWGUIEx
        self.filterLineEdit = OWGUIEx.QLineEditWithActions(self)
        self.filterLineEdit.setPlaceholderText("Filter ...")
        action = QAction(QIcon(os.path.join(orngEnviron.canvasDir,
                        "icons", "delete_gray.png")), "Clear", self)

        self.filterLineEdit.addAction(action, 0, Qt.AlignHCenter)
        self.connect(action, SIGNAL("triggered()"), self.filterLineEdit.clear)

        self.filterCompleter = QCompleter(self.filterLineEdit)
        self.filterCompleter.setCaseSensitivity(Qt.CaseInsensitive)
        self.filterLineEdit.setCompleter(self.filterCompleter)

        hLayout.addWidget(self.filterLineEdit)
        self.mainArea.layout().addWidget(hWidget)

        self.connect(self.filterLineEdit, SIGNAL("textChanged(QString)"),
                     self.filterAnnotationsChartView)

        self.annotationsChartView = MyTreeWidget(self)
        self.annotationsChartView.setHeaderLabels(["Category", "Term",
                            "Count", "Reference count", "P-Value", "Enrichment"])
        self.annotationsChartView.setAlternatingRowColors(True)
        self.annotationsChartView.setSortingEnabled(True)
        self.annotationsChartView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.annotationsChartView.setRootIsDecorated(False)
        self.annotationsChartView.viewport().setMouseTracking(True)
#        self.annotationsChartView.viewport().setAttribute(Qt.WA_Hover)
        self.mainArea.layout().addWidget(self.annotationsChartView)

        contextEventFilter = OWGUI.VisibleHeaderSectionContextEventFilter(self.annotationsChartView)
        self.annotationsChartView.header().installEventFilter(contextEventFilter)

        self.taxid_list = []

        self.connect(self.groupsWidget, SIGNAL("itemClicked(QTreeWidgetItem *, int)"), self.subsetSelectionChanged)

        OWGUI.button(self.controlArea, self, "Commit", callback=self.commit)

        self.loadedGenematcher = "None"
        self.referenceData = None
        self.data = None

        self.treeItems = []

        self.resize(1024, 600)

        self.connect(self, SIGNAL("widgetStateChanged(QString, int, QString)"), self.onStateChange)

        self.updatingAnnotationsFlag = False

    def updateHierarchy(self):
        try:
            self.progressBarInit()
            with orngServerFiles.DownloadProgress.setredirect(self.progressBarSet):
                all, local = obiGeneSets.list_all(), obiGeneSets.list_local()
                organisms = set(obiTaxonomy.essential_taxids() + [t[1] for t in all])
            self.progressBarFinished()

            organism_names = map(name_or_none, organisms)
            organisms = [taxid for taxid, name in zip(organisms, organism_names) \
                         if name is not None]

            self.taxid_list = list(organisms)
            self.speciesComboBox.clear()
            self.speciesComboBox.addItems([obiTaxonomy.name(id) for id in self.taxid_list])
            self.genesets = all
        finally:
            if self.signalManager:
                self.signalManager.freeze(self).pop() #setFreeze(self.signalManager.freezing - 1)

    def setData(self, data=None):
        self.data = data
        self.error(0)
        self.closeContext("")
        self.geneAttrComboBox.clear()
        self.groupsWidget.clear()
        self.annotationsChartView.clear()

        if not getattr(self,"taxid_list", None):
            QTimer.singleShot(100, lambda data=data: self.setData(data))
            return
        if data:
            self.geneAttrs = [attr for attr in data.domain.variables + data.domain.getmetas().values() \
                              if attr.varType != orange.VarTypes.Continuous]

            self.geneAttrComboBox.addItems([attr.name for attr in self.geneAttrs])
            self.geneattr = min(self.geneattr, len(self.geneAttrs) - 1)

            taxid = data_hints.get_hint(data, "taxid", "")
            try:
                self.speciesIndex = self.taxid_list.index(taxid)
            except ValueError, ex:
                pass
            self.genesinrows = data_hints.get_hint(data, "genesinrows", self.genesinrows)

            self.openContext("", data)

#            print self.speciesIndex

            self.setHierarchy(self.getHierarchy(taxid=self.taxid_list[self.speciesIndex]))

            self.loadedGenematcher = "None"
            self.updateAnnotations()

    def setReference(self, data=None):
        self.referenceData = data
        self.referenceRadioBox.setEnabled(bool(data))

    def getHierarchy(self, taxid):
        def recursive_dict():
            return defaultdict(recursive_dict)
        collection = recursive_dict()

        def collect(col, hier):
            if hier:
                collect(col[hier[0]], hier[1:])

        for hierarchy, t_id, _ in self.genesets:
            collect(collection[t_id], hierarchy)
        return collection[taxid]

    def setHierarchy(self, hierarchy):
        self.groupsWidgetItems = {}
        def fill(col, parent, full=()):
            for key, value in sorted(col.items()):
                full_cat = full + (key,)
                item = QTreeWidgetItem(parent, [key])
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                if value:
                    item.setFlags(item.flags() | Qt.ItemIsTristate)

                item.setData(0, Qt.CheckStateRole, QVariant(self.categoriesCheckState.get(full_cat, Qt.Checked)))
                item.setExpanded(True)
                item.category = full_cat
                self.groupsWidgetItems[full_cat] = item
                fill(value, item, full_cat)

        fill(hierarchy, self.groupsWidget)

#    def updateCategoryCounts(self):
#        for cat, item in self.groupWidgetItem:
#            item.setData(1, QVariant(), Qt.DisplayRole)

    def selectedCategories(self):
        taxid = self.taxid_list[self.speciesIndex]
        return [(key, taxid) for key, check in self.getHierarchyCheckState().items() if check == Qt.Checked]

    def getHierarchyCheckState(self):
        def collect(item, full=()):
            checked = item.checkState(0)
            name = str(item.data(0, Qt.DisplayRole).toString())
            full_cat = full + (name,)
            result = [(full_cat, checked)]
            for i in range(item.childCount()):
                result.extend(collect(item.child(i), full_cat))
            return result

        items = [self.groupsWidget.topLevelItem(i) for i in range(self.groupsWidget.topLevelItemCount())]
        states = reduce(list.__add__, [collect(item) for item in items], [])
        return dict(states)

    def subsetSelectionChanged(self, item, column):
        self.categoriesCheckState = self.getHierarchyCheckState()

        categories = self.selectedCategories()
        if not set(categories) <= set(self.currentAnnotatedCategories):
            self.updateAnnotations()
        else:
            self.filterAnnotationsChartView()

    def updateGeneMatcherSettings(self):
        from .OWGOEnrichmentAnalysis import GeneMatcherDialog
        dialog = GeneMatcherDialog(self, defaults=self.geneMatcherSettings, enabled=[True] * 4, modal=True)
        if dialog.exec_():
            self.geneMatcherSettings = [getattr(dialog, item[0]) for item in dialog.items]
            self.loadedGenematcher = "None"
            if self.data:
                self.updateAnnotations()

    def updateGenematcher(self):
        taxid = self.taxid_list[self.speciesIndex]
        if taxid != self.loadedGenematcher:
            self.progressBarInit()
            call = self.asyncCall(obiGene.matcher, name="Gene Matcher", blocking=True, thread=self.thread())
            call.connect(call, SIGNAL("progressChanged(float)"), self.progressBarSet)
            with orngServerFiles.DownloadProgress.setredirect(call.emitProgressChanged):
#            with orngServerFiles.DownloadProgress.setredirect(self.progressBarSet):
                matchers = [obiGene.GMGO, obiGene.GMKEGG, obiGene.GMNCBI, obiGene.GMAffy]
                if any(self.geneMatcherSettings):
                    call.__call__([gm(taxid) for gm, use in zip(matchers, self.geneMatcherSettings) if use])
                    self.genematcher = call.get_result()
#                    self.genematcher = obiGene.matcher([gm(taxid) for gm, use in zip(matchers, self.geneMatcherSettings) if use])
                else:
                    self.genematcher = obiGene.GMDirect()
#                self.genematcher.set_targets(self.referenceGenes())
                self.loadedGenematcher = taxid
            self.progressBarFinished()

    def genesFromExampleTable(self, table):
        if self.genesinrows:
            genes = [attr.name for attr in table.domain.attributes]
        else:
            geneattr = self.geneAttrs[self.geneattr]
            genes = [str(ex[geneattr]) for ex in table]
        return genes

    def clusterGenes(self):
        return self.genesFromExampleTable(self.data)

    def referenceGenes(self):
        if self.referenceData and self.useReferenceData:
            return self.genesFromExampleTable(self.referenceData)
        else:
            taxid = self.taxid_list[self.speciesIndex]
            call = self.asyncCall(obiGene.NCBIGeneInfo, (taxid,), name="Load reference genes", blocking=True, thread=self.thread())
            call.connect(call, SIGNAL("progressChanged(float)"), self.progressBarSet)
            with orngServerFiles.DownloadProgress.setredirect(call.emitProgressChanged):
                call.__call__()
                return call.get_result()

    def _cached_name_lookup(self, func, cache):
        def f(name, cache=cache):
            if name not in cache:
                cache[name] = func(name)
            return cache[name]
        return f

    def mapGeneNames(self, names, cache=None, passUnknown=False):
        if cache is not None:
            umatch = self._cached_name_lookup(self.genematcher.umatch, cache)
        else:
            umatch = self.genematcher.umatch
        if passUnknown:
            return [umatch(name) or name for name in names]
#            return [(mapped_name or name, mapped_name is not None) for mapped_name, name in zip(mapped, names)]
        return [n for n in [umatch(name) for name in names] if n is not None]

    def enrichment(self, geneset, cluster, reference, pval=obiProb.Hypergeometric(), cache=None):
        genes = set(self.mapGeneNames(geneset.genes, cache, passUnknown=False))

        cmapped = genes.intersection(cluster)
        rmapped = genes.intersection(reference)
        return (cmapped, rmapped, pval.p_value(len(cmapped), len(reference), len(rmapped), len(cluster)), float(len(cmapped)) / (len(cluster) or 1) / (float(len(rmapped) or 1) / (len(reference) or 1))) # TODO: compute all statistics here

    def updateAnnotations(self):
        self.updatingAnnotationsFlag = True
        self.annotationsChartView.clear()
        self.error([0, 1])
        if not self.genesinrows and len(self.geneAttrs) == 0:
            self.error(0, "Input data contains no attributes with gene names")
            return

        self.progressBarInit()
        self.updateGenematcher()
        self.currentAnnotatedCategories = categories = self.selectedCategories()

        ## Load collections in a worker thread
        call = self.asyncCall(obiGeneSets.collections, categories, name="Loading collections", blocking=True, thread=self.thread())
        call.connect(call, SIGNAL("progressChanged(float)"), self.progressBarSet)
        with orngServerFiles.DownloadProgress.setredirect(call.emitProgressChanged):
            call.__call__()
            collections = list(call.get_result())

#        with orngServerFiles.DownloadProgress.setredirect(self.progressBarSet):
#            collections = list(obiGeneSets.collections(*categories))
        clusterGenes, referenceGenes = self.clusterGenes(), self.referenceGenes()
        cache = {}

        self.genematcher.set_targets(referenceGenes)

        countAll = len(set(clusterGenes))
        infoText = "%i unique gene names on input\n" % countAll
        referenceGenes = set(self.mapGeneNames(referenceGenes, cache, passUnknown=False))
        self.progressBarSet(1)
        clusterGenes = set(self.mapGeneNames(clusterGenes, cache, passUnknown=False))
        self.progressBarSet(2)
        infoText += "%i (%.1f) gene names matched" % (len(clusterGenes), 100.0 * len(clusterGenes) / countAll)
        self.infoBox.setText(infoText)

        results = []
        from Orange.orng.orngMisc import progressBarMilestones

        milestones = progressBarMilestones(len(collections), 100)
        for i, geneset in enumerate(collections):
            results.append((geneset, self.enrichment(geneset, clusterGenes, referenceGenes, cache=cache)))
            if i in milestones:
                self.progressBarSet(100.0 * i / len(collections))

        if self.useFDR:
            results = sorted(results, key=lambda a:a[1][2])
            pvals = obiProb.FDR([pval for _, (_, _, pval, _) in results])
            results = [(geneset, (cmapped, rmapped, pvals[i], es)) for i, (geneset, (cmapped, rmapped, _, es)) in enumerate(results)]

        fmt = lambda score, max_decimals=10: "%%.%if" % min(int(abs(math.log(max(score, 1e-10)))) + 2, max_decimals) if score > math.pow(10, -max_decimals) and score < 1 else "%.1f"
        self.annotationsChartView.clear()

        maxCount = max([len(cm) for _, (cm, _, _, _) in results] + [1])
        maxRefCount = max([len(rc) for _, (_, rc, _, _) in results] + [1])
        countSpaces = int(math.ceil(math.log10(maxCount)))
        #print maxRefCount
        refSpaces = int(math.ceil(math.log(maxRefCount)))
        countFmt = "%"+str(countSpaces) + "s  (%.2f%%)"
        refFmt = "%"+str(refSpaces) + "s  (%.2f%%)"

        self.filterCompleter.setModel(None)
        linkFont = QFont(self.annotationsChartView.viewOptions().font)
        linkFont.setUnderline(True)
        self.treeItems = []
        for i, (geneset, (cmapped, rmapped, p_val, enrichment)) in enumerate(results):
            if len(cmapped) > 0:
                item = MyTreeWidgetItem(self.annotationsChartView, [" ".join(geneset.hierarchy), geneset.name])
                item.setData(2, Qt.DisplayRole, QVariant(countFmt % (len(cmapped), 100.0*len(cmapped)/countAll)))
                item.setData(2, Qt.ToolTipRole, QVariant(len(cmapped))) # For filtering
                item.setData(3, Qt.DisplayRole, QVariant(refFmt % (len(rmapped), 100.0*len(rmapped)/len(referenceGenes))))
                if p_val > 0.001:
                    item.setData(4, Qt.DisplayRole, QVariant("%0.6f" % p_val))
                else:
                    item.setData(4, Qt.DisplayRole, QVariant("%0.2e" % p_val))
                item.setData(4, 42, QVariant(p_val))
                #stoplec 4 - zelim sort po p_val
                item.setData(4, Qt.ToolTipRole, QVariant("%0.10f" % p_val))
                item.setData(5, Qt.DisplayRole, QVariant(enrichment))
                item.setData(5, Qt.ToolTipRole, QVariant("%.3f" % enrichment))
                item.geneset= geneset
                self.treeItems.append(item)
                if geneset.link:
                    item.setData(1, LinkRole, QVariant(geneset.link))
                    item.setToolTip(1, geneset.link)
                    item.setFont(1, linkFont)
                    item.setForeground(1, QColor(Qt.blue))

        if not self.treeItems:
            self.warning(0, "No enriched sets found.")
        else:
            self.warning(0)

        replace = lambda s:s.replace(",", " ").replace("(", " ").replace(")", " ")
        self._completerModel = completerModel = QStringListModel(sorted(reduce(set.union, [[geneset.name] + replace(geneset.name).split() for geneset, (c, _, _, _) in results if c], set())))
        self.filterCompleter.setModel(completerModel)

        self.annotationsChartView.setItemDelegateForColumn(5, BarItemDelegate(self, scale=(0.0, max(t[1][3] for t in results))))
        self.annotationsChartView.setItemDelegateForColumn(1, LinkStyledItemDelegate(self.annotationsChartView))

        for i in range(self.annotationsChartView.columnCount()):
            self.annotationsChartView.resizeColumnToContents(i)

        self.annotationsChartView.setColumnWidth(1, min(self.annotationsChartView.columnWidth(1), 300))
        self.progressBarFinished()
        QTimer.singleShot(10, self.filterAnnotationsChartView)
        self.updatingAnnotationsFlag = False

    def filterAnnotationsChartView(self, filterString=""):
        if self.updatingAnnotationsFlag:
            return
        categories = set(" ".join(cat) for cat, taxid in self.selectedCategories())
        filterString = str(self.filterLineEdit.text()).lower()
        itemsHidden = []
        for item in self.treeItems:
            item_cat = str(item.data(0, Qt.EditRole).toString())
            count, pval = _toPyObject(item.data(2, Qt.ToolTipRole)), _toPyObject(item.data(4, 42))
            geneset = item.geneset.name.lower()
            hidden = item_cat not in categories or (self.useMinCountFilter and count < self.minClusterCount) or \
                     (self.useMaxPValFilter and pval > self.maxPValue) or filterString not in geneset
            item.setHidden(hidden)
            itemsHidden.append(hidden)

        if self.treeItems and all(itemsHidden):
            self.information(0, "All sets were filtered out.")
        else:
            self.information(0)


    def commit(self):
        selected = self.annotationsChartView.selectedItems()
        genesets = [item.geneset for item in selected]
        cache = {}
        mappedNames = set(self.mapGeneNames(reduce(set.union, [geneset.genes for geneset in genesets], set()), cache))
        if self.genesinrows:
            mapped = [attr for attr in self.data.domain.attributes if self.genematcher.umatch(attr.name) in mappedNames]
            newdomain = orange.Domain(mapped, self.data.domain.classVar)
            newdomain.addmetas(self.data.domain.getmetas())
            data = orange.ExampleTable(newdomain, self.data)
        else:
            geneattr = self.geneAttrs[self.geneattr]
            selected = [1 if self.genematcher.umatch(str(ex[geneattr])) in mappedNames else 0 for ex in self.data]
            data = self.data.select(selected)

#            if self.appendAnnotations:
#                meta = orange.StringVariable("Annotations")
#                data.domain.addmeta(orange.newmetaid(), meta)
#                for ex in data:
#                    geneattr = self.geneAttrs[self.geneattr]
#                    gene = str(ex[geneattr])
#                    annotations = getgene

        self.send("Selected Examples", data)

    def sendReport(self):
        self.reportSettings("Settings", [("Organism", obiTaxonomy.name(self.taxid_list[self.speciesIndex]))])
        self.reportSettings("Filter", [("Min cluster size", self.minClusterCount if self.useMinCountFilter else 0),
                                       ("Max p-value", self.maxPValue if self.useMaxPValFilter else 1.0)])

        self.reportSubsection("Annotations")
        self.reportRaw(reportItemView(self.annotationsChartView))

    def onStateChange(self, stateType, id, text):
        if stateType == "Warning" or stateType == "Info":
            self.annotationsChartView._userMessage = text
            self.annotationsChartView.viewport().update()


def reportItemView(view):
    model = view.model()
    return reportItemModel(view, model)

def reportItemModel(view, model, index=QModelIndex()):
    if not index.isValid() or model.hasChildren(index):
        columnCount, rowCount = model.columnCount(index), model.rowCount(index)
        if not index.isValid():
            text = '<table>\n<tr>' + ''.join('<th>%s</th>' % model.headerData(i, Qt.Horizontal, Qt.DisplayRole).toString() for i in range(columnCount)) +'</tr>\n'
        else:
#            variant = model.data(index, Qt.DisplayRole)
#            text = '<table' + (' caption="%s"' % variant.toString() if variant.isValid() else '') + '>\n'
            pass
        text += ''.join('<tr>' + ''.join('<td>' + reportItemModel(view, model, model.index(row, column, index)) + '</td>' for column in range(columnCount)) + '</tr>\n' for row in range(rowCount) if not view.isRowHidden(row, index))
        text += '</table>'
        return text
    else:
        variant = model.data(index, Qt.DisplayRole)
        return str(variant.toString()) if variant.isValid() else ""



if __name__ == "__main__":
    import cProfile

    app = QApplication(sys.argv)
    w = OWSetEnrichment()
    w.updateHierarchy()
    data = orange.ExampleTable("yeast-class-RPR.tab")
#    data = orange.ExampleTable("../human")
#    print cProfile.runctx("w.setData(data)", globals(), locals())
    w.setData(data)
    w.show()
    app.exec_()
    w.saveSettings()


