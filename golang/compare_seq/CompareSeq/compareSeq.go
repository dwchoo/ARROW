// ComapreSeq/compareSeq.go
package CompareSeq

//package main

import (
	"fmt"
	"strings"
	"sync"
	//"reflect"
)

type letterCompInfo struct {
	loci     int
	letter   string
	misMatch int
}

type SeqCompInfo struct {
	Seq    string
	NumMis int
}

func CompLetters(loci int, qLetter, sLetter string) *letterCompInfo {

	matchCase := letterCompInfo{
		loci:     loci,
		letter:   sLetter,
		misMatch: 0}

	mismatchCase := letterCompInfo{
		loci:     loci,
		letter:   strings.ToLower(sLetter),
		misMatch: 1}

	if qLetter == "N" {
		return &matchCase
	} else if sLetter == "N" {
		return &matchCase
	}

	switch sLetter {
	case "A":
		switch qLetter {
		case "A", "R", "W", "M", "D", "H", "V":
			return &matchCase
		default:
			return &mismatchCase
		}
	case "C":
		switch qLetter {
		case "C", "Y", "S", "M", "B", "H", "V":
			return &matchCase
		default:
			return &mismatchCase
		}
	case "G":
		switch qLetter {
		case "G", "R", "S", "K", "B", "D", "V":
			return &matchCase
		default:
			return &mismatchCase
		}
	case "T":
		switch qLetter {
		case "T", "Y", "W", "K", "B", "D", "H":
			return &matchCase
		default:
			return &mismatchCase
		}
	default:
		return &mismatchCase
	}
}

func CompLettersParall(loci int, qLetter, sLetter string, ch chan<- *letterCompInfo) {
	ch <- CompLetters(loci, qLetter, sLetter)
}

func CompSeq(Query, Seq string) *SeqCompInfo {
	// Check Query and Seq length
	if len(Query) != len(Seq) {
		errString := fmt.Sprintf("Query(%d) and Seq(%d) length different",
			len(Query), len(Seq))
		panic(errString)
	}

	querySlice := strings.Split(Query, "")
	seqSlice := strings.Split(Seq, "")

	//Compare letters parallel
	var CompSlice []letterCompInfo
	letterCh := make(chan *letterCompInfo)
	for loci, qLetter := range querySlice {
		sLetter := seqSlice[loci]
		go CompLettersParall(loci, qLetter, sLetter, letterCh)
		//CompSlice = append(CompSlice,
		//    CompLetters(loci, qLetter,sLetter))
	}
	for i := 0; i < len(querySlice); i++ {
		CompSlice = append(CompSlice, *<-letterCh)
	}
	//fmt.Println(CompSlice)

	//Make changed sequence parallel
	var SeqChangedSlice = make([]string, len(seqSlice))
	var wg sync.WaitGroup
	wg.Add(len(CompSlice))
	for _, letterData := range CompSlice {
		go func(letterData letterCompInfo, SeqSlice []string) {
			defer wg.Done()
			//tmpLoci := letterData.loci
			//tmpLetter := letterData.letter
			SeqSlice[letterData.loci] = letterData.letter
		}(letterData, SeqChangedSlice)
	}
	wg.Wait()

	SeqChanged := strings.Join(SeqChangedSlice, "")
	//fmt.Println(SeqChanged)

	//Sum mismatches
	var NumMis int = 0
	for _, letterData := range CompSlice {
		NumMis += letterData.misMatch
	}
	//fmt.Println(NumMis)
	return &SeqCompInfo{Seq: SeqChanged, NumMis: NumMis}

}

func CompSeqParall(Query, Seq string, ch chan<- *SeqCompInfo) {
	ch <- CompSeq(Query, Seq)
}

func CompQuery2Seqs(Query string, SeqSlice []string, IdxSlice []int) *[]SeqCompInfo {
	if len(SeqSlice) != len(IdxSlice) {
		errString := fmt.Sprintf("Index(%d) and Seq(%d) length different",
			len(IdxSlice), len(SeqSlice))
		panic(errString)
	}

	var results []SeqCompInfo
	//var wg sync.WaitGroup
	//seqInfoCh := make(chan *SeqCompInfo)
	seqLength := len(SeqSlice)
	seqInfoChs := make(map[int](chan *SeqCompInfo))
	//wg.Add(seqLength)
	for i := 0; i < seqLength; i++ {
		idx := IdxSlice[i]
		seq := SeqSlice[i]
		seqInfoChs[idx] = make(chan *SeqCompInfo)
		go CompSeqParall(Query, seq, seqInfoChs[idx])
	}
	//fmt.Println("Finished parallel")
	//wg.Wait()

	for _, idx := range IdxSlice {
		results = append(results, *<-seqInfoChs[idx])
	}
	return &results

}

func main_tmp() {
	query := "CCAGAAGCCTTTCCGTGCCTNGG"
	seq := "ATAGAAGCCTTTCCGTGCCTAGG"
	fmt.Println(query)
	fmt.Println(seq)
	CompInfo := CompSeq(query, seq)
	fmt.Println(CompInfo)
	////seqSlice := []rune(seq)

	seqSlice := []string{
		"CCAGAAGgCTaTtCaTcCaTGGG",
		"gCAGAAGCtccaCCGTcCCTCGG",
		"CCAGAcGCCaTcCtGTGCCcTGG",
		"CCAGcAGCCTcTtCGTGggTTGG",
		"CCAGAgGCagTgCCGTGtCcCGG",
		"CCAGcAGCaccTtgGTGCCTGGG",
		"CCAGccaCCaTcCaGTGCCTGGG",
		"CCAGAgGCCTTggCcaGCCaAGG",
		"CgAGAcaCCgTgCCcTGCCTTGG",
		"aCAGAAGCCTTgggGTGCCcCGG"}
	var indexSlice []int
	var upperSeqSlices []string
	for idx, seq := range seqSlice {
		upperString := strings.ToUpper(seq)
		upperSeqSlices = append(upperSeqSlices, upperString)
		indexSlice = append(indexSlice, idx)
	}
	fmt.Println(indexSlice)
	result := CompQuery2Seqs(query, upperSeqSlices, indexSlice)
	//fmt.Println(result)
	for idx, out := range *result {
		fmt.Println(out)
		fmt.Println(bool(seqSlice[idx] == out.Seq))
	}

}

func main() {
	//main_tmp()

}
