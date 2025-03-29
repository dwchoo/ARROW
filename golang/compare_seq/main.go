package main

import (
	"C"
	"time"

	"github.com/compare_seq/CompareSeq"
)
import (
	"fmt"
)

type SeqCompInfo = CompareSeq.SeqCompInfo

// CompQuerySeqs
func CompQuerySeqs(Query string, Seq *[]string, Index *[]int) ([]string, []int) {
	var SeqSlice []string
	var MMSlice []int
	//var tmpIndexSlice []int
	//for _, idx := range Index {
	//	tmpIndexSlice = append(tmpIndexSlice, *idx)
	//}
	results := CompareSeq.CompQuery2Seqs(Query, *Seq, *Index)

	for _, data := range *results {
		SeqSlice = append(SeqSlice, data.Seq)
		MMSlice = append(MMSlice, data.NumMis)
	}

	return SeqSlice, MMSlice
}

//export ReturnSeqs
func ReturnSeqs(Query string, DataPath string) []string {

	seqSlice, indexSlice := CompareSeq.ReadCSV(&DataPath)

	_, _ = CompQuerySeqs(Query, seqSlice, indexSlice)
	fmt.Println("Run ReturnSeqs end all")
	return []string{"hi", "my"}
}

//export ReturnMMs
func ReturnMMs(Query string, DataPath string) string {
	seqSlice, indexSlice := CompareSeq.ReadCSV(&DataPath)
	_, _ = CompQuerySeqs(Query, seqSlice, indexSlice)
	return "End game"
}

//export ResultSaveCSV
func ResultSaveCSV(filePath string, Query string, DataPath string) string {
	seqSlice, indexSlice := CompareSeq.ReadCSV(&DataPath)
	Seqs, MMs := CompQuerySeqs(Query, seqSlice, indexSlice)
	CompareSeq.WriteCSVfromSlice(filePath, indexSlice, &Seqs, &MMs)

	return filePath
}

func tmp_main() {
	startTime := time.Now()
	dataPath := "data.csv"
	_, _ = CompareSeq.ReadCSV(&dataPath)

	fmt.Println("Load data : ", time.Since(startTime))
	loadTime := time.Now()

	query := "CCAGAAGCCTTTCCGTGCCTNGG"
	//returnIdx, returnSeq, returnMM := CompQuerySeqs(query, seqSlice, indexSlice)
	//fmt.Println(result)
	_ = ReturnSeqs(query, dataPath)
	fmt.Println("Seq processing : ", time.Since(loadTime))
	sqTime := time.Now()

	_ = ReturnMMs(query, dataPath)
	fmt.Println("MM processing : ", time.Since(sqTime))
	//mmTime := time.Now()

	saveCsvTime := time.Now()
	ResultSaveCSV("SaveFromGo.csv", query, dataPath)
	fmt.Println("SaveAsCsv processing : ", time.Since(saveCsvTime))

}

func main() {
	tmp_main()
}
