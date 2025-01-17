# -*- coding: utf-8 -*-
import json
import zipfile

from convlab2.dst.sumbt.multiwoz_zh.sumbt_config import *


def trans_value(value):
    trans = {
        "": "未提及",
        "没有提到": "未提及",
        "没有": "未提及",
        "未提到": "未提及",
        "一个也没有": "未提及",
        "无": "未提及",
        "是的": "有",
        "不是": "没有",
        "不关心": "不在意",
        "不在乎": "不在意",
    }

    return trans.get(value, value)


def convert_to_glue_format(data_dir, sumbt_dir):

    if not os.path.isdir(os.path.join(sumbt_dir, args.tmp_data_dir)):
        os.mkdir(os.path.join(sumbt_dir, args.tmp_data_dir))

    ### Read ontology file
    with open(os.path.join(data_dir, "ontology.json"), "r") as fp_ont:
        data_ont = json.load(fp_ont)
        ontology = {}
        for domain_slot in data_ont:
            domain, slot = domain_slot.split("-")
            if domain not in ontology:
                ontology[domain] = {}
            ontology[domain][slot] = {}
            for value in data_ont[domain_slot]:
                ontology[domain][slot][value] = 1

    ### Read woz logs and write to tsv files
    if os.path.exists(os.path.join(sumbt_dir, args.tmp_data_dir, "train.tsv")):
        print("data has been processed!")
        return 0
    print("begin processing data")

    fp_train = open(
        os.path.join(sumbt_dir, args.tmp_data_dir, "train.tsv"), "w"
    )
    fp_dev = open(os.path.join(sumbt_dir, args.tmp_data_dir, "dev.tsv"), "w")
    fp_test = open(os.path.join(sumbt_dir, args.tmp_data_dir, "test.tsv"), "w")

    fp_train.write(
        "# Dialogue ID\tTurn Index\tUser Utterance\tSystem Response\t"
    )
    fp_dev.write(
        "# Dialogue ID\tTurn Index\tUser Utterance\tSystem Response\t"
    )
    fp_test.write(
        "# Dialogue ID\tTurn Index\tUser Utterance\tSystem Response\t"
    )

    for domain in sorted(ontology.keys()):
        for slot in sorted(ontology[domain].keys()):
            fp_train.write(str(domain) + "-" + str(slot) + "\t")
            fp_dev.write(str(domain) + "-" + str(slot) + "\t")
            fp_test.write(str(domain) + "-" + str(slot) + "\t")

    fp_train.write("\n")
    fp_dev.write("\n")
    fp_test.write("\n")

    # fp_data = open(os.path.join(SELF_DATA_DIR, "data.json"), "r")
    # data = json.load(fp_data)

    file_split = ["train", "val", "test"]
    fp = [fp_train, fp_dev, fp_test]

    for split_type, split_fp in zip(file_split, fp):

        zipfile_name = "{}.json.zip".format(split_type)
        zip_fp = zipfile.ZipFile(os.path.join(data_dir, zipfile_name))
        data = json.loads(str(zip_fp.read(zip_fp.namelist()[0]), "utf-8"))

        for file_id in data:
            user_utterance = ""
            system_response = ""
            turn_idx = 0
            for idx, turn in enumerate(data[file_id]["log"]):
                if idx % 2 == 0:  # user turn
                    user_utterance = data[file_id]["log"][idx]["text"]
                else:  # system turn
                    user_utterance = user_utterance.replace("\t", " ")
                    user_utterance = user_utterance.replace("\n", " ")
                    user_utterance = user_utterance.replace("  ", " ")

                    system_response = system_response.replace("\t", " ")
                    system_response = system_response.replace("\n", " ")
                    system_response = system_response.replace("  ", " ")

                    split_fp.write(str(file_id))  # 0: dialogue ID
                    split_fp.write("\t" + str(turn_idx))  # 1: turn index
                    split_fp.write(
                        "\t" + str(user_utterance)
                    )  # 2: user utterance
                    split_fp.write(
                        "\t" + str(system_response)
                    )  # 3: system response

                    belief = {}

                    for domain in data[file_id]["log"][idx]["metadata"].keys():
                        for slot in data[file_id]["log"][idx]["metadata"][
                            domain
                        ]["semi"].keys():
                            value = data[file_id]["log"][idx]["metadata"][
                                domain
                            ]["semi"][slot].strip()
                            # value = value_trans.get(value, value)
                            value = trans_value(value)

                            if domain not in ontology:
                                print("domain (%s) is not defined" % domain)
                                continue

                            if slot not in ontology[domain]:
                                print(
                                    "slot (%s) in domain (%s) is not defined"
                                    % (slot, domain)
                                )  # bus-arriveBy not defined
                                continue

                            if (
                                value not in ontology[domain][slot]
                                and value != "未提及"
                            ):
                                print(
                                    "%s: value (%s) in domain (%s) slot (%s) is not defined in ontology"
                                    % (file_id, value, domain, slot)
                                )
                                value = "未提及"

                            belief[str(domain) + "-" + str(slot)] = value

                        for slot in data[file_id]["log"][idx]["metadata"][
                            domain
                        ]["book"].keys():
                            if slot == "booked":
                                continue
                            if (
                                domain == "公共汽车"
                                and slot == "人数"
                                or domain == "列车"
                                and slot == "票价"
                            ):
                                continue  # not defined in ontology

                            value = data[file_id]["log"][idx]["metadata"][
                                domain
                            ]["book"][slot].strip()
                            value = trans_value(value)

                            if str("预订" + slot) not in ontology[domain]:
                                print(
                                    "预订%s is not defined in domain %s"
                                    % (slot, domain)
                                )
                                continue

                            if (
                                value not in ontology[domain]["预订" + slot]
                                and value != "未提及"
                            ):
                                print(
                                    "%s: value (%s) in domain (%s) slot (预订%s) is not defined in ontology"
                                    % (file_id, value, domain, slot)
                                )
                                value = "未提及"

                            belief[str(domain) + "-预订" + str(slot)] = value

                    for domain in sorted(ontology.keys()):
                        for slot in sorted(ontology[domain].keys()):
                            key = str(domain) + "-" + str(slot)
                            if key in belief:
                                split_fp.write("\t" + belief[key])
                            else:
                                split_fp.write("\t未提及")

                    split_fp.write("\n")
                    split_fp.flush()

                    system_response = data[file_id]["log"][idx]["text"]
                    turn_idx += 1

    fp_train.close()
    fp_dev.close()
    fp_test.close()

    print("data has been processed!")
