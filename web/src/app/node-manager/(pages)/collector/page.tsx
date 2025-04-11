"use client";
import React, { useEffect, useState, useRef } from "react";
import collectorstyle from "./index.module.scss";
import { Segmented, Menu } from "antd";
import useApiClient from '@/utils/request';
import useApiCollector from "@/app/node-manager/api/collector/index";
import EntityList from "@/components/entity-list/index";
import { useRouter } from "next/navigation";
import { useTranslation } from "@/utils/i18n";
import type { CardItem } from "@/app/node-manager/types/collector";
import CollectorModal from "./collectorModal";
import { ModalRef } from "@/app/node-manager/types";
import { useMenuItem } from "@/app/node-manager/constants/collector";
import { Option } from "@/types";

const Collector = () => {
  const router = useRouter();
  const { t } = useTranslation();
  const { isLoading } = useApiClient();
  const { getCollectorlist, getControllerList } = useApiCollector();
  const modalRef = useRef<ModalRef>(null);
  const [value, setValue] = useState<string | number>('collector');
  const [controllerCards, setControllerCards] = useState<CardItem[]>([]);
  const [collectorCards, setCollectorCards] = useState<CardItem[]>([]);
  const [controllerCount, setControllerCount] = useState<number>(0);
  const [collectorCount, setCollectorCount] = useState<number>(0);
  const [selected, setSelected] = useState<string[]>([]);
  const [search, setSearch] = useState<string>('');
  const [options, setOptions] = useState<Option[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const menuItem = useMenuItem();
  const titleItem = [
    {
      label: `${t('node-manager.collector.collector')}(${collectorCount})`,
      value: 'collector',
    },
    {
      label: `${t('node-manager.collector.controller')}(${controllerCount})`,
      value: 'controller',
    },
  ];

  useEffect(() => {
    if (!isLoading) {
      fetchCollectorlist();
    }
  }, [isLoading])

  useEffect(() => {
    fetchCollectorlist(search, selected);
  }, [value])

  const navigateToCollectorDetail = (item: CardItem) => {
    router.push(`
      /node-manager/collector/detail?id=${item.id}&name=${item.name}&introduction=${item.description}&system=${item.tagList[0]}`);
  };

  const cardSetters: Record<string, React.Dispatch<React.SetStateAction<CardItem[]>>> = {
    controller: setControllerCards,
    collector: setCollectorCards,
  };

  const filterBySelected = (data: any[], selected: string[]) => {
    if (!selected?.length) return data;
    const selectedSet = new Set(selected);
    return data.filter((item) =>
      item.tagList.every((tag: string) => selectedSet.has(tag))
    );
  };

  const handleResult = (res: any, value: string, selected?: string[]) => {
    const optionSet = new Set<string>();
    const _options: Option[] = [];
    let tempdata = res.map((item: any) => {
      const system = item.node_operating_system || item.os;
      if (system && !optionSet.has(system)) {
        optionSet.add(system);
        _options.push({ value: system, label: system });
      }
      return ({
        id: item.id,
        name: item.name,
        service_type: item.service_type,
        executable_path: item.executable_path,
        execute_parameters: item.execute_parameters,
        description: item.introduction || '--',
        icon: 'caijiqizongshu',
        tagList: [system]
      })
    });
    tempdata = filterBySelected(tempdata, selected || []);
    cardSetters[value](tempdata);
    setOptions(_options);
  }

  const fetchCollectorlist = async (search?: string, selected?: string[]) => {
    const params = {
      name: search
    }
    try {
      setLoading(true);
      const res = await Promise.all([getControllerList(params), getCollectorlist(params)]);
      const controllerList = res[0];
      const collectorList = res[1];
      setControllerCount(controllerList.length);
      setCollectorCount(collectorList.length);
      handleResult(controllerList, 'controller', selected);
      handleResult(collectorList, 'collector', selected);
      setLoading(false);
    } catch (error) {
      console.log(error)
    }
  };

  const openModal = (config: any) => {
    modalRef.current?.showModal({
      title: config?.title,
      type: config?.type,
      form: config?.form,
      key: config?.key
    })
  };

  const handleSubmit = () => {
    fetchCollectorlist();
  };

  const menuActions = (data: any) => {
    return (<Menu
      onClick={(e) => e.domEvent.preventDefault()}
    >
      {menuItem.map((item) => {
        if (value === 'controller' && ['delete', 'edit'].includes(item.key)) return;
        return (
          <Menu.Item
            key={item.title}
            onClick={() => openModal({ ...item.config, form: data, key: value })}>{t(`node-manager.collector.${item.title}`)}
          </Menu.Item>
        )
      }
      )}
    </Menu>)
  };

  const changeFilter = (selected: string[]) => {
    fetchCollectorlist('', selected);
    setSelected(selected);
  };

  const ifOpenAddModal = () => {
    if (value === 'collector') {
      return {
        openModal: () => openModal({ title: 'addCollector', type: 'add', form: {} })
      }
    }
  };

  const onSearch = (search: string) => {
    setSearch(search);
    fetchCollectorlist(search, selected);
  };

  return (
    <div className={`${collectorstyle.collection}`}>
      {/* 顶部的提示信息 */}
      <Segmented
        className="custom-tabs"
        options={titleItem}
        defaultValue='collector'
        onChange={(value) => setValue(value)}
      />
      {/* 卡片的渲染 */}
      <EntityList
        data={value === 'controller' ? controllerCards : collectorCards}
        loading={loading}
        menuActions={(value) => menuActions(value)}
        filter filterOptions={options} changeFilter={changeFilter}
        {...ifOpenAddModal()}
        onSearch={onSearch}
        onCardClick={(item: CardItem) => navigateToCollectorDetail(item)}></EntityList>
      <CollectorModal ref={modalRef} onSuccess={handleSubmit} />
    </div>
  );
}

export default Collector;
