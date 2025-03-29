// CompareSeq/load_data.go
package CompareSeq

import (
	"bufio"
	"encoding/csv"
	"fmt"
	"os"
	"strconv"
	"strings"
	//"reflect"
)

//var ctx = context.Background()

//func LoadParquet(filePath string) (*dataframe.DataFrame, error) {
//	//dataframe.Read
//	var err error
//	var fr source.ParquetFile
//	var df *dataframe.DataFrame
//
//	fr, err = local.NewLocalFileReader(filePath)
//	if err != nil {
//		return nil, err
//	}
//	defer fr.Close()
//	df, err = imports.LoadFromParquet(ctx, fr)
//	if err != nil {
//		return nil, err
//	}
//	//fmt.Println(df.Table())
//	return df, err
//}
//
//func ReturnSeqIndex(df *dataframe.DataFrame, idx string, col string) ([]int, []string) {
//	var indexSlice []int
//	var seqSlice []string
//	iterator := df.ValuesIterator(dataframe.ValuesOptions{0, 1, true})
//	df.Lock()
//	for {
//		row, vals, _ := iterator()
//		if row == nil {
//			break
//		}
//		//fmt.Println(*row, vals["index"], vals["seq"])
//		indexSlice = append(indexSlice, int(vals[idx].(int64)))
//		seqSlice = append(seqSlice, strings.ToUpper(vals[col].(string)))
//
//	}
//	return indexSlice, seqSlice
//}

func ReadCSV(filePath *string) (*[]string, *[]int) {
	var err error
	var SeqSlice []string
	var IndexSlice []int
	csvFile, err := os.Open(*filePath)
	if err != nil {
		fmt.Println(err)
	}
	//fmt.Println("Successfully Opened CSV file")
	defer csvFile.Close()

	csvLines, err := csv.NewReader(csvFile).ReadAll()
	indexCol := 0
	seqCol := 1
	_, err = strconv.Atoi(csvLines[3][indexCol])
	if err != nil {
		indexCol = 1
		seqCol = 0
	}
	for _, seq := range csvLines {
		tmpIndex, err := strconv.Atoi(seq[indexCol])
		tmpSeq := strings.ToUpper(seq[seqCol])
		if err != nil {
			continue
		}
		SeqSlice = append(SeqSlice, tmpSeq)
		IndexSlice = append(IndexSlice, tmpIndex)
	}

	//for idx, seq := range SeqSlice {
	//	fmt.Println(seq, IndexSlice[idx])
	//	if idx == 10 {
	//		break
	//	}
	//}
	return &SeqSlice, &IndexSlice
}
func WriteCSVfromSlice(filePath string, indexSlice *[]int, seqSlice *[]string, MMSlice *[]int) {
	file, err := os.Create(filePath)
	if err != nil {
		panic(err)
	}
	wr := csv.NewWriter(bufio.NewWriter(file))

	wr.Write([]string{"index", "seq", "mismatch"})
	for idx, seq := range *seqSlice {
		stringIndex := strconv.Itoa((*indexSlice)[idx])
		stringMM := strconv.Itoa((*MMSlice)[idx])
		wr.Write([]string{stringIndex, seq, stringMM})
	}
	wr.Flush()
}

func tmp_main() {
	//tmpPath := "./../data.parquet"
	//df, err := LoadParquet(tmpPath)
	//fmt.Println(err)

	//indexSlice, seqSlice := ReturnSeqIndex(df, "index", "seq")
	//for idx, indexSlice := range indexSlice {
	//	fmt.Println(indexSlice, seqSlice[idx])
	//}

	tmpPath := "./../data.csv"
	ReadCSV(&tmpPath)

}

//func main() {
//	tmp_main()
//}
